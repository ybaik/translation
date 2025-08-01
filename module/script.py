import json
from pathlib import Path
from typing import List, Dict, Tuple
from module.font_table import FontTable
from module.decoding import decode, encode


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
                code_hex = f"{code_int:02X}"
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
                    if "�" not in sentence:  # Need to check this later
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

    # Check if decoding is needed
    encoding = script.pop("encoding", None)
    if encoding is not None:
        data = decode(data, encoding)

    # Check if custom codes exist
    custom_codes = script.pop("custom_codes", None)
    if custom_codes is not None:
        font_table.set_custom_code_1byte(custom_codes)

    # Write scripts
    for address, sentence in script.items():
        [code_hex_start, code_hex_end] = address.split("=")
        spos = int(code_hex_start, 16)
        epos = int(code_hex_end, 16)
        pos = spos

        # Check if there is a unsupport letter in the sentence
        skip_sentence = False
        check_1byte = False
        for character in sentence:
            if character == "|":
                check_1byte = True
                continue
            if check_1byte:
                if not font_table.exists_1byte(character):
                    skip_sentence = True
                    break
                check_1byte = False
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
                    assert (
                        0
                    ), f"{code_hex_start}:{character} is not in the 1-byte font table."
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

    # Check if encoding is needed
    if encoding is not None:
        data = encode(data, encoding)

    return data, valid_sentence_count


def write_script_multibyte(
    data: bytearray, font_table: FontTable, script: Dict
) -> bytearray:

    valid_sentence_count = 0

    # Write scripts
    for address, sentence in script.items():
        [code_hex_start, code_hex_end] = address.split("=")
        spos = int(code_hex_start, 16)
        epos = int(code_hex_end, 16)
        pos = spos

        # Check if there is a unsupport letter in the sentence
        skip_sentence = False
        for character in sentence:
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

            if font_table.get_code(character) is None:
                assert 0, f"{character} is not in the font table."

            code_hex = font_table.get_code(character)
            code_int = int(code_hex, 16)

            # Check if the letter is a one byte character
            if len(code_hex) == 2:
                data[pos] = code_int
                pos += 1
            else:  # Input two bytes character
                code1 = (code_int & 0xFF00) >> 8
                code2 = code_int & 0x00FF
                data[pos] = code1
                data[pos + 1] = code2
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


def split_sentence(script: Dict, font_table: FontTable, control_code: str):
    pop_list = []
    new_dict = dict()
    for address, sentence in script.items():
        if control_code not in sentence:
            continue
        pop_list.append(address)

        hex_start, hex_end = address.split("=")
        spos = int(hex_start, 16)
        epos = int(hex_end, 16)

        # Check previous sentence
        pos = sentence.find(control_code)
        code_length = len(control_code)

        sentence_prev_full = sentence[: pos + code_length]
        sentence_prev = sentence[:pos]
        length_prev_full = font_table.check_length_from_sentence(sentence_prev_full)
        length = font_table.check_length_from_sentence(sentence_prev)
        spos_prev = spos
        epos_prev = spos + length - 1

        # Check post sentence
        sentence_post = sentence[pos + code_length :]
        spos_post = spos + length_prev_full
        epos_post = epos

        if len(sentence_post):
            new_dict[f"{spos_post:05X}={epos_post:05X}"] = sentence_post

            # Recursive function
            if control_code in sentence_post:
                split_sentence(new_dict, font_table, control_code)

        new_dict[f"{spos_prev:05X}={epos_prev:05X}"] = sentence_prev

    for key in pop_list:
        del script[key]

    script.update(new_dict)


def split_sentences(
    script: Dict, font_table: FontTable, control_codes: List[str] = []
) -> Dict:
    for control_code in control_codes:
        pop_list = []
        update_dict = dict()
        for addresses, sentence in script.items():
            if control_code not in sentence:
                continue
            pop_list.append(addresses)

            new_dict = {addresses: sentence}
            split_sentence(new_dict, font_table, control_code)
            update_dict.update(new_dict)

        # Remove original sentences when they are split
        for adresses in pop_list:
            del script[adresses]
        script.update(update_dict)

    return script


class Script:
    def __init__(self, file_path: str) -> None:
        self.script = None
        self.encoding = None
        self.custom_codes = None
        self.custom_input = None

        # Read a script
        if not Path(file_path).exists():
            print(f"{file_path} does not exist.")
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            self.script = json.load(f)

        # Get encoding
        if "encoding" in self.script.keys():
            self.encoding = self.script.pop("encoding")

        # Get custom codes
        if "custom_codes" in self.script.keys():
            self.custom_codes = self.script.pop("custom_codes")

        # Get custom input
        if "custom_input" in self.script.keys():
            self.custom_input = self.script.pop("custom_input")

    def set_custom_codes(self, custom_codes: Dict) -> None:
        self.custom_codes = custom_codes

    def save(self, file_path: str) -> None:

        save_dict = dict()

        # Set encoding
        if self.encoding is not None:
            save_dict["encoding"] = self.encoding

        # Set custom codes
        if self.custom_codes is not None:
            save_dict["custom_codes"] = self.custom_codes

        # Set custom input
        if self.custom_input is not None:
            save_dict["custom_input"] = self.custom_input

        save_dict.update(self.script)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(save_dict, f, ensure_ascii=False, indent=4)

    def validate(self, font_table: FontTable) -> bool:
        # Check script
        count_false_length = 0
        count_false_characters = 0

        for address, sentence in self.script.items():
            if "=" not in address:
                continue
            length_from_address = font_table.check_length_from_address(address)
            length_from_sentence = font_table.check_length_from_sentence(sentence)
            if length_from_address != length_from_sentence:
                print(
                    f"Wrong sentence length:{address}: {length_from_address}-{length_from_sentence}"
                )
                count_false_length += 1

            # Check if there is false characters in a sentence via comparison with the font table
            count_false_character, false_character = font_table.verify_sentence(
                sentence
            )
            if count_false_character:
                # print(f"Wrong letters:{address}: {count_false_character}-{false_character}")
                count_false_characters += count_false_character
                # Debug
                count_false_characters = 0

        return count_false_length, count_false_characters

    def split_sentences(self, font_table: FontTable, split_code: str) -> bool:

        # Initialize remove_key_list, modified_script
        remove_key_list = []
        modified_script = dict()
        # Connect sentences
        for address, sentence in self.script.items():

            # Check if the address is alreeady checked
            if address in remove_key_list:
                continue

            # Check there is a split code in the sentence
            split_index = sentence.find(split_code)

            if split_index == -1 or split_index + 1 == len(sentence):
                continue

            # Set a merged sentencee
            remove_key_list.append(address)

            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)

            sentence_prev = sentence[: split_index + 1]
            sentence_next = sentence[split_index + 1 :]

            length_prev = font_table.check_length_from_sentence(sentence_prev)

            epos_prev = spos + length_prev - 1
            spos_next = epos_prev + 1

            address_prev = f"{spos:05X}={epos_prev:05X}"
            address_next = f"{spos_next:05X}={epos:05X}"

            modified_script[address_prev] = sentence_prev
            modified_script[address_next] = sentence_next

        if len(remove_key_list) == 0:
            print("No sentences are split.")
            return False

        # Remove old sentences
        for key in remove_key_list:
            del self.script[key]

        # Update script
        self.script.update(modified_script)
        self.script = dict(sorted(self.script.items()))

        return True

    def merge_sentences(self) -> bool:

        # Initialize remove_key_list, modified_script
        remove_key_list = []
        modified_script = dict()

        # Set a temporal start_pos_table
        start_pos_table = dict()
        for address in self.script.keys():
            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)
            start_pos_table[spos] = address

        # Connect sentences
        for address, sentence in self.script.items():

            # Check if the address is alreeady checked
            if address in remove_key_list:
                continue

            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)

            # Check if the next sentence exists
            if start_pos_table.get(epos + 1) is None:
                continue

            # Set a merged sentencee
            address_next = start_pos_table[epos + 1]
            remove_key_list.append(address)
            remove_key_list.append(address_next)

            epos_next = int(address_next.split("=")[-1], 16)

            address_new = f"{spos:05X}={epos_next:05X}"
            sentence_new = sentence + self.script[address_next]
            modified_script[address_new] = sentence_new

        if len(remove_key_list) == 0:
            print("No sentences are merged.")
            return False

        # Remove old sentences
        for key in remove_key_list:
            del self.script[key]

        # Update script
        self.script.update(modified_script)
        self.script = dict(sorted(self.script.items()))

        return True

    def attach_control_codes(self, binay_path: str, control_codes: Dict = {}) -> bool:

        # Check control codes
        if len(control_codes.keys()) == 0:
            print("No control codes are specified.")
            return

        # Read a binary data
        if not Path(binay_path).exists():
            print(f"{binay_path} does not exist.")
            return

        with open(binay_path, "rb") as f:
            binary_data = f.read()
        binary_data = bytearray(binary_data)

        # Decoding bianry data
        if self.encoding is not None:
            binary_data = decode(binary_data, self.encoding)

        # Initialize remove_key_list, modified_script
        remove_key_list = []
        modified_script = dict()

        # Set a temporal start_pos_table
        start_pos_table = dict()
        for address in self.script.keys():
            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)
            start_pos_table[spos] = address

        # Connect sentences
        for address, sentence in self.script.items():

            # Check if the address is alreeady checked
            if address in remove_key_list:
                continue

            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)
            if epos + 1 >= len(binary_data):
                continue

            # Check if the next character is a control code
            char_code_hex = f"{binary_data[epos + 1]:02X}"
            if char_code_hex not in control_codes.keys():
                continue

            # Set a merged sentencee
            remove_key_list.append(address)
            epos_next = epos + 1

            address_new = f"{spos:05X}={epos_next:05X}"
            sentence_new = sentence + "|" + control_codes[char_code_hex]
            modified_script[address_new] = sentence_new

        if len(remove_key_list) == 0:
            print("No sentences are connected.")
            return False

        # Remove old sentences
        for key in remove_key_list:
            del self.script[key]

        # Update script
        self.script.update(modified_script)
        self.script = dict(sorted(self.script.items()))

        return True

    def filter_sentences(self) -> bool:
        """
        To get rid of 1-byte noisy characters
        """

        remove_key_list = []
        modified_script = dict()

        for address, sentence in self.script.items():
            if "=" not in address:
                continue
            if "|" not in sentence:
                continue

            start, end = address.split("=")
            start = int(start, 16)  # Convert to integer
            end = int(end, 16)  # Convert to integer

            is_1byte = False
            remove = ""
            add_byte = 0
            for character in sentence:
                if character == "|":
                    is_1byte = True
                    continue

                if is_1byte:
                    if character == "C":
                        is_1byte = False
                        break
                    else:
                        remove += f"|{character}"
                        add_byte += 1
                        is_1byte = False
                else:
                    break

            if add_byte > 0:
                remove_key_list.append(address)
                start_new = start + add_byte
                if start_new >= end:
                    continue
                address_new = f"{start_new:05X}={end:05X}"
                sentence_new = sentence[add_byte * 2 :]
                modified_script[address_new] = sentence_new

        if len(remove_key_list) == 0:
            print("No sentences are connected.")
            return False

        # Remove old sentences
        for key in remove_key_list:
            del self.script[key]

        # Update script
        self.script.update(modified_script)
        self.script = dict(sorted(self.script.items()))

        return True
