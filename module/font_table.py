import os
import json
from typing import List
from .sjis_code import is_sjis_valid


def check_file(path: str) -> bool:
    if os.path.exists(path):
        return True
    print(f"{path} does not exist.")
    return False


class FontTable:
    def __init__(self, file_path: str) -> None:
        # Initialize
        self.code2char = dict()
        self.char2code = dict()
        self.code_int_min = 0xFFFF
        self.code_int_max = 0

        # For 1-byte characters
        self.char2code_1byte = dict()

        # Read font table
        self.read_font_table(file_path)

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
            print("f{ext} is not a supported format.")
            return False

        # make char2code table
        self.char2code = dict()
        for k, v in self.code2char.items():
            if len(k) == 2:  # 1-byte code
                if self.char2code_1byte.get(v) is None:
                    self.char2code_1byte[v] = k
                else:
                    print(f"Invalid 1-byte code: {k}")
            else:
                if self.char2code.get(v) is None:
                    self.char2code[v] = k
                else:
                    print(f"Invalid 2-byte code: {k}")

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
        for code in codes:
            if not is_sjis_valid(code):
                print(f"code {code} is invalid for sjis.")

        codes.sort()
        self.code_int_min = int(codes[0], 16)
        self.code_int_max = int(codes[-1], 16)
        self.code2char = font_table

    def _read_tbl(self, file_path: str) -> None:

        font_table = dict()

        # read font table
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip()
                idx = line.find("=")
                code_hex = line[:idx].upper()
                character = line[idx + 1 :]

                # check if the code is value based on shift-jis
                if not is_sjis_valid(code_hex):
                    print(f"code {code_hex} is invalid for sjis.")

                if font_table.get(code_hex) is None:
                    font_table[code_hex] = character
                else:
                    print(f"duplicated: {code_hex}")

        codes = list(font_table.keys())
        codes.sort()
        self.code_int_min = int(codes[0], 16)
        self.code_int_max = int(codes[-1], 16)
        self.code2char = font_table

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

    def get_char(self, code_hex: str) -> str:
        return self.code2char.get(code_hex)

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

    def get_code_1byte(self, character: str) -> str:
        return self.char2code_1byte.get(character)

    def get_codes(self, sentence: str) -> List[str]:
        codes_hex = []
        for character in sentence:
            code_hex = self.char2code.get(character)
            codes_hex.append(code_hex)

        return codes_hex
