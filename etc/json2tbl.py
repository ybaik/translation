from font_table import check_file, read_font_table


def main():

    json_font_table_path = 'font_table/anex86.json'
    tbl_font_table_path = 'anex86.tbl'

    table_for_tbl = ''

    # read a font table
    if not check_file(json_font_table_path): return 
    font_table, _, _ = read_font_table(json_font_table_path)
    
    print(len(font_table))

    for code, letter in font_table.items():
        table_for_tbl += f'{code}={letter}\n'

    with open(tbl_font_table_path, 'w') as f:
        f.write(table_for_tbl)


if __name__ == "__main__":
    main()
