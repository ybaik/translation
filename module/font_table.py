import os
import json

'''
def uint(val):
    if val < 0:
        return val + (1<<32)
    return val
'''

def check_file(path):
    if not os.path.exists(path):
        print(f'No {path} exist')
        return False
    return True

class FontTable:
    def __init__(self, file_path: str):
        # initialize 
        self.code2char = None
        self.char2code = None
        self.code_int_min = 0xffff
        self.code_int_max = 0

        # read font table
        self.read_font_table(file_path)

    def read_font_table(self, file_path: str):

        if not os.path.isfile(file_path):
            print(f'No {file_path} exist.')
            return False

        ext = file_path.split('.')[-1]
        if ext == 'tbl':
            self.read_tbl(file_path)
        elif ext == 'json': 
            self.read_json(file_path)
        else:
            print('f{ext} is not a supported format.')
            return False

        # make char2code table
        char2code = dict()
        for k, v in self.code2char.items():
            if char2code.get(v) is None:
                char2code[v] = k
        self.char2code = char2code
        return True

    def read_json(self, file_path: str):

        with open(file_path) as f:
            font_table = json.load(f)

        codes = list(font_table.keys())
        self.code_int_min = int(codes[0], 16)
        self.code_int_max = int(codes[-1], 16)
        self.code2char = font_table

    def read_tbl(self, file_path: str):

        font_table = dict()
        code_int_min = 0xffff
        code_int_max = 0

        # read font table
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip()
                code_hex, character = line.split('=')
                code_int = int(code_hex, 16)
                code_hex = hex(code_int)

                code_int_min = min(code_int_min, code_int)
                code_int_max = max(code_int_max, code_int)

                if font_table.get(code_hex) is None:
                    font_table[code_hex] = character
                else:
                    print(f'duplicated: {code_hex}')

        self.code2char = font_table
        self.code_int_min = code_int_min
        self.code_int_max = code_int_max
    
    def range(self, code_int: int):
        return True if self.code_int_min <= code_int <= self.code_int_max else False

    def get_char(self, code_hex: str):
        if '0x' not in code_hex:
            code_hex = '0x' + code_hex
        return self.code2char.get(code_hex)

    def get_chars(self, codes_hex): # list
        word = ''
        for code_hex in codes_hex:
            code_hex = code_hex.lower()
            if '0x' not in code_hex:
                code_hex = '0x' + code_hex
            if self.code2char.get(code_hex):
                word += self.code2char.get(code_hex)
            else:
                word += '@'
        return word

    def get_code(self, letter: str):
        return self.char2code.get(letter)

    def get_codes(self, script: str):
        codes_hex = []
        for letter in script:
            code_hex = self.char2code.get(letter)
            codes_hex.append(code_hex)

        return codes_hex

'''
def read_tbl(file_path):
    font_table = dict()
    code_int_min = 0xffff
    code_int_max = 0

    # read font table
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.rstrip()
            code_hex, character = line.split('=')
            code_int = int(code_hex, 16)
            code_hex = hex(code_int)

            code_int_min = min(code_int_min, code_int)
            code_int_max = max(code_int_max, code_int)

            if font_table.get(code_hex) is None:
                font_table[code_hex] = character
            else:
                print(f'duplicated: {code_hex}')
    return font_table, code_int_min, code_int_max


def read_json(file_path):

    with open(file_path) as f:
        font_table = json.load(f)

    codes = list(font_table.keys())
    code_int_min = int(codes[0], 16)
    code_int_max = int(codes[-1], 16)

    return font_table, code_int_min, code_int_max


def read_font_table(file_path):
    ext = file_path.split('.')[-1]
    if ext == 'tbl':
        return read_tbl(file_path)
    elif ext == 'json':
        return read_json(file_path)

    print('f{ext} is not a supported format')
'''
