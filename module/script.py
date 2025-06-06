from typing import Dict, Tuple
from .font_table import FontTable
from .sjis_code import is_sjis_valid


def extract_scripts(
    data: bytearray,
    font_table: FontTable,
    length_threshold: int,
    restriction: bool = False,
) -> Tuple[Dict, Dict]:

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
                address = f"{i-length*2:05X}={i-1:05X}"
                script[address] = sentence
                if sentence_log:
                    script_log[address] = sentence_log
            sentence = ""
            sentence_log = ""
            length = 0
        i += 1

    # check a result of the end of data
    if length >= length_threshold:
        address = f"{i-length*2:05X}={i-1:05X}"
        script[address] = sentence
        if sentence_log:
            script_log[address] = sentence_log
        sentence = ""
        sentence_log = ""
        length = 0

    return script, script_log


def write_scripts(data: bytearray, font_table: FontTable, scripts: Dict) -> bytearray:

    # write scripts
    for address, sentence in scripts.items():
        [code_hex_start, code_hex_end] = address.split("=")
        spos = int(code_hex_start, 16)
        epos = int(code_hex_end, 16)
        pos = spos

        # write characters in the sentence
        idx_char = 0
        while idx_char < len(sentence):
            character = sentence[idx_char]

            # Check if the letter is a one byte character
            if character == "|":
                idx_char += 1
                character = sentence[idx_char]

                if font_table.get_code_1byte(character) is not None:
                    code_hex = font_table.get_code_1byte(character)
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

    return data


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


def extract_table(
    data: bytearray, scripts: Dict, font_table: FontTable = dict()
) -> FontTable:

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


def find_sentence(script: Dict, sentence: str) -> bool:
    """Find a sentence.

    Args:
        script (dict): A dictionary of scripts.
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
        script (dict): A dictionary of scripts.
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
