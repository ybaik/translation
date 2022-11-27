from module.font_table import FontTable


def main():

    json_font_table_path = "font_table/font_table-jpn.json"
    tbl_font_table_path = "font_table-jpn.tbl"

    font_table = FontTable(json_font_table_path)
    font_table.write_font_table(tbl_font_table_path)


if __name__ == "__main__":
    main()
