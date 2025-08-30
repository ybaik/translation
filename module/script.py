import json
from pathlib import Path
from typing import Dict, Tuple
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
                        address = f"{i - length:05X}={i - 1:05X}"
                        script[address] = sentence
                        if sentence_log:
                            script_log[address] = sentence_log
                sentence = ""
                sentence_log = ""
                length = 0
            i += 1

    # Check a result of the end of data
    if length >= length_threshold:
        address = f"{i - length * 2:05X}={i - 1:05X}"
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

    # Check if custom inputs exist
    custom_input = script.pop("custom_input", None)
    if custom_input is not None:
        for address, codes in custom_input.items():
            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)

            # Need to isolate descriptions
            codes = codes.split("#")[0]

            # Check if the format is right
            num_codes = epos - spos + 1
            if len(codes) != num_codes * 2:
                assert 0, f"The length of custom input is not matched. {address}:{len(codes)} != {num_codes}"

            for i in range(num_codes):
                code_int = int(codes[i * 2 : i * 2 + 2], 16)
                data[spos + i] = code_int

    # Write scripts
    for address, sentence in script.items():
        # Check if there is a unsupproted address format
        if "=" not in address:
            assert 0, f"{address} is not in the correct format."

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
                    assert 0, f"{code_hex_start}:{character} is not in the 1-byte font table."
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


def write_script_multibyte(data: bytearray, font_table: FontTable, script: Dict) -> bytearray:
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


def write_code(data: bytearray, hex_start: str, hex_end: str, code_hex: str, count: int) -> bytearray:
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


def write_code_1byte(data: bytearray, hex_start: str, hex_end: str, code_hex: str, count: int) -> bytearray:
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


def extract_table(data: bytearray, script: Dict, font_table: FontTable = dict()) -> FontTable:
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


class Script:
    def __init__(self, file_path: str = "") -> None:
        self.script = dict()
        self.encoding = None
        self.custom_codes = None
        self.custom_input = None

        # Read a script if the file path is specified
        if len(file_path):
            if Path(file_path).exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    self.script = json.load(f)
            else:
                assert 0, f"{file_path} does not exist."

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
        """Set custom codes
        Args:
            custom_codes (Dict): A dictionary of custom codes.
        """
        self.custom_codes = custom_codes

    def set_address_padding(self, address_padding: int = 5) -> None:
        """Set address padding
        Args:
            address_padding (int): A padding length of address.
        """
        annoying = []
        for address in self.script.keys():
            start, end = address.split("=")
            if len(start) != address_padding:
                annoying.append(address)
                continue
            if len(end) != address_padding:
                annoying.append(address)
                continue

        for address in annoying:
            sentence = self.script.pop(address)
            start, end = address.split("=")
            start_int = int(start, 16)
            end_int = int(end, 16)
            new_address = f"{start_int:0{address_padding}X}={end_int:0{address_padding}X}"
            self.script[new_address] = sentence

    def save(self, file_path: str, address_padding: int = 5) -> None:
        """Save the script to a file
        Args:
            file_path (str): A path to a file.
        """
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

        # Set address padding
        self.set_address_padding(address_padding)

        # Sort by keys (address) for the main script
        self.script = dict(sorted(self.script.items()))

        save_dict.update(self.script)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(save_dict, f, ensure_ascii=False, indent=4)

    def add_script(self, script: Dict) -> None:
        """Add a script to the main script
        Args:
            script (Dict): A script.
        """
        self.script.update(script)

    def validate(self, font_table: FontTable) -> bool:
        """Check the script
        Args:
            font_table (FontTable): A font table.
        Returns:
            bool: True if the script is valid.
        """
        # Check script
        count_false_length = 0
        count_false_characters = 0

        if self.custom_codes is not None:
            font_table.set_custom_code(self.custom_codes)

        for address, sentence in self.script.items():
            if "=" not in address:
                continue
            length_from_address = font_table.check_length_from_address(address)
            length_from_sentence = font_table.check_length_from_sentence(sentence)
            if length_from_address != length_from_sentence:
                print(f"Wrong sentence length:{address}: {length_from_address}-{length_from_sentence}")
                count_false_length += 1

            # Check if there is false characters in a sentence via comparison with the font table
            count_false_character, false_character = font_table.verify_sentence(sentence)
            if count_false_character:
                print(f"Wrong letters:{address}: {count_false_character}-{false_character}")
                count_false_characters += count_false_character

        return count_false_length, count_false_characters

    def validate_with_binary(self, font_table: FontTable, binary_path: Path) -> bool:
        """Check the script with a binary data
        Args:
            binary_path (Path): A binary data path.
        Returns:
            bool: True if the script is valid.
        """
        # Read a binary data
        if not Path(binary_path).exists():
            print(f"{binary_path} does not exist.")
            return

        with open(binary_path, "rb") as f:
            binary_data = f.read()
        binary_data = bytearray(binary_data)

        # Decoding bianry data
        if self.encoding is not None:
            binary_data = decode(binary_data, self.encoding)

        # Font table update
        if self.custom_codes is not None:
            font_table.set_custom_code(self.custom_codes)

        diff_status = False
        err_reason = ""
        for address, sentence in self.script.items():
            if "=" not in address:
                continue

            spos = int(address.split("=")[0], 16)

            is_diff = False

            # Need to add a routine to check if the sentence is hex-only or not
            if "0x:" == sentence[:3]:
                codes = sentence[3:].split("#")[0]
                length = len(codes) // 2
                for i in range(length):
                    code_int = int(codes[i * 2 : i * 2 + 2], 16)
                    if code_int != binary_data[spos + i]:
                        is_diff = True
                        break
            else:
                idx = 0
                is_1byte = False
                for letter in sentence:
                    if letter == "|":
                        is_1byte = True
                        continue
                    if is_1byte:
                        code_hex = font_table.get_code_ascii(letter)
                        code_bin_int = binary_data[spos + idx]
                        code_bin_hex = f"{code_bin_int:02X}"
                        if code_hex != code_bin_hex:
                            is_diff = True
                            err_reason = f"{code_hex}/{code_bin_hex}"
                            break
                        else:
                            idx += 1
                            is_1byte = False
                    else:
                        code_hex = font_table.get_code(letter)
                        code_bin_int = (binary_data[spos + idx] << 8) + binary_data[spos + idx + 1]
                        code_bin_hex = f"{code_bin_int:04X}"
                        if code_hex != code_bin_hex:
                            is_diff = True
                            err_reason = f"{code_hex}/{code_bin_hex}"
                            break
                        else:
                            idx += 2
            if is_diff:
                print(f"{address}:{sentence} - {err_reason}")

                diff_status = True
        return diff_status

    def split_sentences(self, font_table: FontTable, split_code: str) -> bool:
        """Split sentences by a split code
        Args:
            font_table (FontTable): A font table.
            split_code (str): A split code.
        Returns:
            bool: True if the sentences are split.
        """
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
        """Merge sentences if addresses of two sentences are consecutive without duplication
        Returns:
            bool: True if the sentences are merged.
        """
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

    def attach_control_codes(self, binary_path: str, control_codes: Dict = {}) -> bool:
        # Check control codes
        if len(control_codes.keys()) == 0:
            print("No control codes are specified.")
            return

        # Read a binary data
        if not Path(binary_path).exists():
            print(f"{binary_path} does not exist.")
            return

        with open(binary_path, "rb") as f:
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

    def filter_given_sentence(self, given_sentence: str) -> bool:
        """
        To get rid of a given sentence
        """
        remove_key_list = []
        for address, sentence in self.script.items():
            if sentence != given_sentence:
                continue
            remove_key_list.append(address)

        if len(remove_key_list) == 0:
            print("No sentences are removed.")
            return False

        # Remove old sentences
        for key in remove_key_list:
            del self.script[key]

        return True

    def extract_script(
        self,
        data: bytearray,
        font_table: FontTable,
        length_threshold: int,
        check_ascii: bool = False,
        check_ascii_restriction: bool = False,
        check_range: bool = False,
    ) -> Dict:
        """Extract a script from a binary data
        Args:
            data (bytearray): A binary data.
            font_table (FontTable): A font table.
            length_threshold (int): A threshold of the length of a sentence.
            check_ascii (bool): If True, check if the sentence contains only ASCII characters.
            check_ascii_restriction (bool): If True, check if the sentence contains only ASCII characters and the first character is not '_'.
            check_range (bool): If True, check if the sentence contains only characters in the font table.
        Returns:
            Dict: A dictionary of a script log.
        """

        i = 0
        length = 0  # Sentence length in bytes
        sentence = ""
        sentence_log = ""
        self.script = dict()
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
                            address = f"{i - length:05X}={i - 1:05X}"
                            self.script[address] = sentence
                            if sentence_log:
                                script_log[address] = sentence_log
                    sentence = ""
                    sentence_log = ""
                    length = 0
                i += 1

        # Check a result of the end of data
        if length >= length_threshold:
            address = f"{i - length * 2:05X}={i - 1:05X}"
            self.script[address] = sentence
            if sentence_log:
                script_log[address] = sentence_log
            sentence = ""
            sentence_log = ""
            length = 0

        return script_log

    def write_script(self, data: bytearray, font_table: FontTable) -> bytearray:
        valid_sentence_count = 0

        # Check if decoding is needed
        if self.encoding is not None:
            data = decode(data, self.encoding)

        # Check if custom codes exist
        if self.custom_codes is not None:
            font_table.set_custom_code(self.custom_codes)

        # Check if custom inputs exist
        if self.custom_input is not None:
            for address, codes in self.custom_input.items():
                [code_hex_start, code_hex_end] = address.split("=")
                spos = int(code_hex_start, 16)
                epos = int(code_hex_end, 16)

                # Need to isolate descriptions
                codes = codes.split("#")[0]
                codes = codes.replace("0x:", "")

                # Check if the format is right
                num_codes = epos - spos + 1
                if len(codes) != num_codes * 2:
                    assert 0, f"The length of custom input is not matched. {address}:{len(codes)} != {num_codes}"

                for i in range(num_codes):
                    code_int = int(codes[i * 2 : i * 2 + 2], 16)
                    data[spos + i] = code_int

        # Write scripts
        for address, sentence in self.script.items():
            # Check if there is a unsupproted address format
            if "=" not in address:
                assert 0, f"{address} is not in the correct format."

            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)
            pos = spos

            # Check if the setence is hex-only
            if "0x:" == sentence[:3]:
                # Need to isolate descriptions
                codes = sentence[3:].split("#")[0]

                # Check if the format is right
                num_codes = epos - spos + 1
                if len(codes) != num_codes * 2:
                    assert 0, f"The length of custom input is not matched. {address}:{len(codes)} != {num_codes}"

                for i in range(num_codes):
                    code_int = int(codes[i * 2 : i * 2 + 2], 16)
                    data[spos + i] = code_int

                valid_sentence_count += 1
                continue

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
                        assert 0, f"{code_hex_start}:{character} is not in the 1-byte font table."
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
        if self.encoding is not None:
            data = encode(data, self.encoding)

        return data, valid_sentence_count
