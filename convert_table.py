from module.font_table import FontTable


def main():

    # json_font_table_path = 'font_table/anex86.json'
    # tbl_font_table_path = 'anex86.tbl'
    json_font_table_path = "d:/work_han/font_KCT_dos.json"
    tbl_font_table_path = "d:/work_han/font_KCT_dos_.tbl"

    font_table = FontTable(json_font_table_path)
    font_table.write_font_table(tbl_font_table_path)


if __name__ == "__main__":
    main()
