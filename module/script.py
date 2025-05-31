from .sjis_code import is_sjis_valid


def extract_scripts(data, font_table, length_threshold, restriction=False):

    i = 0
    length = 0  # sentence length
    sentence = ""
    sentence_log = ""
    script = dict()
    script_log = dict()

    while i < len(data) - 1:
        # extract a 2byte code
        code_int = (data[i] << 8) + data[i + 1]
        code_hex = f"{code_int:X}"

        need_to_stop = True

        if restriction:
            if is_sjis_valid(code_hex):
                need_to_stop = False
        else:
            if font_table.range(code_int):
                need_to_stop = False

        if not need_to_stop:
            # find a character in the font table
            character = font_table.get_char(code_hex)

            if character:  # character is in the font table
                sentence += character
                if character == "■":
                    sentence_log += f":{code_hex}" if sentence_log else f"{code_hex}"
                length += 1
                i += 1
            else:
                sentence += "@"
                sentence_log += f":@{code_hex}" if sentence_log else f"@{code_hex}"
                length += 1
                i += 1
        else:
            # check sentence length and save
            if length >= length_threshold:
                address = f"{i-length*2:X}={i-1:X}"
                script[address] = sentence
                if sentence_log:
                    script_log[address] = sentence_log
            sentence = ""
            sentence_log = ""
            length = 0
        i += 1

    # check a result of the end of data
    if length >= length_threshold:
        address = f"{i-length*2:X}={i-1:X}"
        script[address] = sentence
        if sentence_log:
            script_log[address] = sentence_log
        sentence = ""
        sentence_log = ""
        length = 0

    return script, script_log


def write_scripts(data, font_table, scripts):

    # write scripts
    for range, sentence in scripts.items():
        [code_hex_start, code_hex_end] = range.split("=")
        spos = int(code_hex_start, 16)
        epos = int(code_hex_end, 16)
        pos = spos
        # write letters in the sentence
        for letter in sentence:
            if font_table.get_code(letter) is not None:
                code_hex = font_table.get_code(letter)
                code_int = int(code_hex, 16)

                code1 = (code_int & 0xFF00) >> 8
                code2 = code_int & 0x00FF
                data[pos] = code1
                data[pos + 1] = code2
            else:
                assert 0, f"{letter} is not in the font table."
            pos += 2

    return data


def write_code(data, hex_start, hex_end, code_hex, count):

    spos = int(hex_start, 16)
    epos = int(hex_end, 16)
    pos = spos

    for i in range(count):
        if pos >= epos:
            break

        code_int = int(code_hex, 16)
        code_int += i
        code1 = (code_int & 0xFF00) >> 8
        code2 = code_int & 0x00FF
        data[pos] = code1
        data[pos + 1] = code2
        pos += 2

    return data


def extract_table(data, scripts, font_table=dict()):

    # write scripts
    for range, sentence in scripts.items():
        [code_hex_start, code_hex_end] = range.split("=")
        spos = int(code_hex_start, 16)
        pos = spos

        # write letters in the sentence
        for i, letter in enumerate(sentence):
            # extract a 2byte code
            code_int = (data[pos] << 8) + data[pos + 1]
            code_hex = f"{code_int:X}"

            if font_table.get(code_hex) is None:
                font_table[code_hex] = letter
            pos += 2

    return font_table


def find_dialogue(script: dict, dialogue: str) -> bool:
    """Find a dialogue.

    Args:
        script (dict): A dictionary of scripts.
        dialogue (str): A dialogue to find.

    Returns:
        bool: True if the dialogue is found.
    """

    found = False
    for key, value in script.items():
        if value == dialogue:
            found = True

    return found


def find_dialogue_and_update(script: dict, dialogue: str, new_dialogue: str) -> bool:
    """Find a dialogue and update it.

    Args:
        script (dict): A dictionary of scripts.
        dialogue (str): A dialogue to find.
        new_dialogue (str): A new dialogue to update. The length should be matched.

    Returns:
        bool: True if the dialogue is found and updated.
    """

    dlength = len(dialogue)
    nlength = len(new_dialogue)
    if dlength != nlength:
        assert 0, f"Dialogue length is not matched. {dlength} != {nlength}"

    is_updated = False
    for key, value in script.items():
        if value == dialogue:
            script[key] = new_dialogue
            is_updated = True

    return is_updated
