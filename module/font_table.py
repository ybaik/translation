import os
import json
from copy import deepcopy
from typing import List, Dict, Tuple
from .jisx0201 import jisx0201_table


class FontTable:
    def __init__(self, file_path: str) -> None:
        # Initialize
        self.code2char = dict()
        self.char2code = dict()
        self.code_int_min = 0xFFFF
        self.code_int_max = 0

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} does not exist.")

        # Set code 1 byte (jisx0201)
        self.code2char_ascii = deepcopy(jisx0201_table)
        self.char2code_ascii = {v: k for k, v in self.code2char_ascii.items()}

        # Read font table
        self.read_font_table(file_path)

    def set_custom_code(self, custom_codes: Dict = {}) -> None:
        update_1byte = False
        update_2byte = False
        for k, v in custom_codes.items():
            if len(k) == 2:  # 1-byte code
                old_code = self.char2code_ascii.get(v, None)
                if old_code is not None:
                    # To avoid duplicated code and letter
                    self.code2char_ascii.pop(old_code, None)
                self.code2char_ascii[k] = v
                update_1byte = True
            elif len(k) == 4:  # 2-byte code
                old_code = self.char2code.get(v, None)  # To avoid duplicated code and letter
                if old_code is not None:
                    # To avoid duplicated code and letter
                    self.code2char.pop(old_code, None)
                self.code2char[k] = v
                update_2byte = True
            else:
                raise ValueError(f"Invalid code length: {k} during custom code setting.")

        if update_1byte:
            self.char2code_ascii = {v: k for k, v in self.code2char_ascii.items()}
        if update_2byte:
            self.char2code = dict()
            for k, v in self.code2char.items():
                self.char2code.setdefault(v, k)

    def read_font_table(self, file_path: str) -> bool:
        if not os.path.isfile(file_path):
            print(f"No {file_path} exist.")
            return False
        _, ext = os.path.splitext(file_path)
        if ext == ".tbl":
            self._read_tbl(file_path)
        elif ext == ".json":
            self._read_json(file_path)
        else:
            print(f"{ext} is not a supported format.")
            return False

        # Make char2code table
        self.char2code = dict()
        for k, v in self.code2char.items():
            self.char2code.setdefault(v, k)

        return True

    def write_font_table(self, file_path: str) -> bool:
        if self.code2char is None:
            print("No font table to write.")
            return False

        _, ext = os.path.splitext(file_path)
        if ext == ".tbl":
            self._write_tbl(file_path)
        elif ext == ".json":
            self._write_json(file_path)
        else:
            print("f{ext} is not a supported format.")
            return False
        return True

    def _read_json(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            font_table = json.load(f)

        codes = list(font_table.keys())
        codes.sort()
        self.code_int_min = int(codes[0], 16)
        self.code_int_max = int(codes[-1], 16)
        self.code2char = font_table

    def _read_tbl(self, file_path: str) -> None:
        font_table = dict()

        # Read font table
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip()
                idx = line.find("=")
                code_hex = line[:idx].upper()
                character = line[idx + 1 :]

                if font_table.get(code_hex) is None:
                    font_table[code_hex] = character
                else:
                    print(f"duplicated: {code_hex}")

        codes = list(font_table.keys())
        codes.sort()
        self.code_int_min = int(codes[0], 16)
        self.code_int_max = int(codes[-1], 16)
        self.code2char = font_table

    def _read_tbl_1byte(self, file_path: str) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

            # Reset 1-byte table
            self.code2char_ascii = dict()
            self.char2code_ascii = dict()

            for line in lines:
                line = line.rstrip()
                idx = line.find("=")
                code_hex = line[:idx].upper()
                character = line[idx + 1 :]

                if self.code2char.get(code_hex) is None:
                    self.code2char_ascii[code_hex] = character
                    self.char2code_ascii[character] = code_hex
                else:
                    print(f"duplicated: {code_hex}")

    def _write_json(self, file_path: str) -> None:
        font_table = dict(sorted(self.code2char.items()))
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(font_table, f, ensure_ascii=False, indent=2)

    def _write_tbl(self, file_path: str) -> None:
        table_for_tbl = ""
        for code, letter in sorted(self.code2char.items()):
            table_for_tbl += f"{code}={letter}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(table_for_tbl)

    def range(self, code_int: int) -> bool:
        return True if self.code_int_min <= code_int <= self.code_int_max else False

    def exists(self, character: str) -> bool:
        return character in self.char2code.keys()

    def exists_1byte(self, character: str) -> bool:
        return character in self.char2code_ascii.keys()

    def is_japanese(self, character: str) -> bool:
        code = self.char2code.get(character)
        code_int = int(code, 16)
        if code_int >= 0x829F and code_int <= 0x8396:
            return True
        return False

    def get_char(self, code_hex: str) -> str:
        return self.code2char.get(code_hex)

    def get_char_ascii(self, code_hex: str) -> str:
        return self.code2char_ascii.get(code_hex)

    def get_chars(self, codes_hex) -> str:
        word = ""
        for code_hex in codes_hex:
            if self.code2char.get(code_hex):
                word += self.code2char.get(code_hex)
            else:
                word += "@"
        return word

    def get_code(self, character: str) -> str:
        return self.char2code.get(character)

    def get_code_ascii(self, character: str) -> str:
        return self.char2code_ascii.get(character)

    def get_codes(self, sentence: str) -> List[str]:
        codes_hex = []
        for character in sentence:
            code_hex = self.char2code.get(character)
            codes_hex.append(code_hex)

        return codes_hex

    def check_length_from_address(self, address: str) -> int:
        [code_hex_start, code_hex_end] = address.split("=")
        length_from_address = int(code_hex_end, 16) - int(code_hex_start, 16) + 1
        return length_from_address

    def check_length_from_sentence(self, sentence: str) -> int:
        # Check if the sentence is hex-only
        if "0x:" == sentence[:3]:
            sentence = sentence[3:].split("#")[0]  # Remove the hex-only code and the comment
            return len(sentence) // 2

        num_one_byte = sentence.count("|")
        num_two_byte = len(sentence) - num_one_byte * 2
        length_from_sentence = num_one_byte + num_two_byte * 2
        return length_from_sentence

    def check_length_from_table(self, sentence: str) -> int:
        length = 0
        for letter in sentence:
            code = self.get_code(letter)
            length += len(code) // 2
        return length

    def verify_sentence(self, sentence: str) -> Tuple[bool, str]:
        count_false_character = 0
        false_characters = ""
        check_ascii = False

        if "0x:" != sentence[:3]:
            for character in sentence:
                if character == "|":
                    check_ascii = True
                    continue

                if check_ascii:
                    if self.char2code_ascii.get(character) is None:
                        count_false_character += 1
                        false_characters += "|" + character
                    check_ascii = False
                    continue

                if character == "@":  # an ignore character
                    continue

                if character not in self.char2code:
                    count_false_character += 1
                    false_characters += character

        return count_false_character, false_characters
