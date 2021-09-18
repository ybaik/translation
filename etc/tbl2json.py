import json
#from font_table import check_file, read_font_table


def main():

    tbl_font_table_path = '../macross.tbl'
    json_font_table_path = '../anex86.json'
    json_font_table_path_new = '../anex86dos.json'

    # read json font table
    #if not check_file(json_font_table_path): return  
    #font_table, _, _ = read_font_table(json_font_table_path)

    font_table = dict()

    with open(tbl_font_table_path, 'rb') as f:
        for line in f:
            line = line.decode(encoding='cp949')
            line = line.replace('\r\n', '')
            code, letter = line.split('=')
            code_int = int(code, 16)
            code_hex = hex(code_int)
            print(code_hex)

            if letter == '\u3000':
                letter = '■'

            if font_table.get(code_hex) is not None:
                character = font_table.get(code_hex)

                if letter == '■' and character != '■':
                    print(code_hex, letter, character)

                    print('a')
            else:
                font_table[code_hex] = letter

    font_table = dict(sorted(font_table.items()))
    with open(json_font_table_path_new, 'w') as f:
        json.dump(font_table, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
