import os
import json


def check_file(path):
    if not os.path.exists(path):
        print(f'No {path} exist')
        return False
    return True


def uint(val):
    if val < 0:
        return val + (1<<32)
    return val


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

