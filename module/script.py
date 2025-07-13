from typing import Dict, Tuple
from module.font_table import FontTable


def extract_script(
    data: bytearray,
    font_table: FontTable,
    length_threshold: int,
    check_ascii: bool = False,
    check_ascii_restriction: bool = False,
    check_range: bool = False,
) -> Tuple[Dict, Dict]:

    i = 0
    length = 0  # Sentence length in bytes
    sentence = ""
    sentence_log = ""
    script = dict()
    script_log = dict()

    while i < len(data) - 1:
        # Extract a 2byte code
        code_int = (data[i] << 8) + data[i + 1]
        code_hex = f"{code_int:X}"

        need_to_stop = True

        character = font_table.get_char(code_hex)
        if character is not None:
            need_to_stop = False

        if check_range and font_table.range(code_int):
            need_to_stop = False

        if not need_to_stop:
            # Find a character in the font table
            character = font_table.get_char(code_hex)

            if character:  # Character is in the font table
                sentence += character
                if character == "■":
                    sentence_log += f":{code_hex}" if sentence_log else f"{code_hex}"
                length += 2
                i += 2
            else:
                sentence += "@"
                sentence_log += f":@{code_hex}" if sentence_log else f"@{code_hex}"
                length += 2
                i += 2
        else:
            if check_ascii:
                code_int = data[i]
                code_hex = f"{code_int:X}"
                character = font_table.get_char_ascii(code_hex)

                if check_ascii_restriction and character != "_" and length == 0:
                    need_to_stop = True
                elif character is not None:
                    sentence += "|" + character
                    length += 1
                    need_to_stop = False

            # Check sentence length and save
            if need_to_stop:
                if length >= length_threshold:
                    address = f"{i-length:05X}={i-1:05X}"
                    script[address] = sentence
                    if sentence_log:
                        script_log[address] = sentence_log
                sentence = ""
                sentence_log = ""
                length = 0
            i += 1

    # Check a result of the end of data
    if length >= length_threshold:
        address = f"{i-length*2:05X}={i-1:05X}"
        script[address] = sentence
        if sentence_log:
            script_log[address] = sentence_log
        sentence = ""
        sentence_log = ""
        length = 0

    return script, script_log


def write_script(data: bytearray, font_table: FontTable, script: Dict) -> bytearray:

    valid_sentence_count = 0

    # Write scripts
    for address, sentence in script.items():
        [code_hex_start, code_hex_end] = address.split("=")
        spos = int(code_hex_start, 16)
        epos = int(code_hex_end, 16)
        pos = spos

        # Check if there is a unsupport letter in the sentence
        skip_sentence = False
        skip_character = False
        for character in sentence:
            if character == "|":
                skip_character = True
                continue
            if skip_character:
                skip_character = False
                continue
            if not font_table.exists(character):
                skip_sentence = True
                break

            if font_table.is_japanese(character):
                skip_sentence = True
                break
        if skip_sentence:
            continue
        valid_sentence_count += 1

        # Write characters in the sentence
        idx_char = 0
        while idx_char < len(sentence):
            character = sentence[idx_char]

            # Check if the letter is a one byte character
            if character == "|":
                idx_char += 1
                character = sentence[idx_char]

                if font_table.get_code_ascii(character) is not None:
                    code_hex = font_table.get_code_ascii(character)
                    code_int = int(code_hex, 16)
                    data[pos] = code_int
                else:
                    assert 0, f"{character} is not in the 1-byte font table."
                pos += 1
            else:  # Input two bytes character
                if character in ["■", "@"]:
                    pass
                if font_table.get_code(character) is not None:
                    code_hex = font_table.get_code(character)
                    code_int = int(code_hex, 16)

                    code1 = (code_int & 0xFF00) >> 8
                    code2 = code_int & 0x00FF
                    data[pos] = code1
                    data[pos + 1] = code2
                else:
                    assert 0, f"{character} is not in the 2-byte font table."
                pos += 2
            idx_char += 1

    return data, valid_sentence_count


def write_code(
    data: bytearray, hex_start: str, hex_end: str, code_hex: str, count: int
) -> bytearray:

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


def write_code_1byte(
    data: bytearray, hex_start: str, hex_end: str, code_hex: str, count: int
) -> bytearray:

    spos = int(hex_start, 16)
    epos = int(hex_end, 16)
    pos = spos

    for i in range(count):
        if pos >= epos:
            break

        code_int = int(code_hex, 16)
        code_int += i
        data[pos] = code_int
        pos += 1

    return data


def extract_table(
    data: bytearray, script: Dict, font_table: FontTable = dict()
) -> FontTable:

    # Check a script
    for range, sentence in script.items():
        [code_hex_start, code_hex_end] = range.split("=")
        spos = int(code_hex_start, 16)
        pos = spos

        # Check letters in the sentence
        for letter in sentence:
            # extract a 2byte code
            code_int = (data[pos] << 8) + data[pos + 1]
            code_hex = f"{code_int:X}"

            if font_table.get(code_hex) is None:
                font_table[code_hex] = letter
            pos += 2

    return font_table


def find_sentence(script: Dict, sentence: str) -> bool:
    """Find a sentence.

    Args:
        script (dict): A dictionary of a script.
        sentence (str): A sentence to find.

    Returns:
        bool: True if the sentence is found.
    """

    found = False
    for key, value in script.items():
        if value == sentence:
            found = True

    return found


def find_sentence_and_update(script: Dict, sentence: str, new_sentence: str) -> bool:
    """Find a sentence and update it.

    Args:
        script (dict): A dictionary of script.
        sentence (str): A sentence to find.
        new_sentence (str): A new sentence to update. The length should be matched.

    Returns:
        bool: True if the sentence is found and updated.
    """

    dlength = len(sentence)
    nlength = len(new_sentence)
    if dlength != nlength:
        assert 0, f"sentence length is not matched. {dlength} != {nlength}"

    is_updated = False
    for key, value in script.items():
        if value == sentence:
            script[key] = new_sentence
            is_updated = True

    return is_updated
