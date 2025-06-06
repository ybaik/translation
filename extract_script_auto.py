import os
import json
from pathlib import Path
from module.font_table import check_file, FontTable
from module.script import extract_scripts


def main():

    bin_path = "../workspace/m4_jpn_s"
    font_table_path = "font_table/font_table-jpn-40K.json"
    extended_word = "_jpn"
    script_path = "../workspace/m4_jpn_s4"

    length_threshold = 2
    restriction = False
    # =================================================================

    files = os.listdir(bin_path)

    for file in files:
        src_data_path = f"{bin_path}/{file}"
        dst_script_path = f"{script_path}/{file}{extended_word}.json"

        if not os.path.isfile(src_data_path):
            continue

        print(f"{file} ===========================================")
        # read a font table
        if not check_file(font_table_path):
            return
        font_table = FontTable(font_table_path)

        # read the target (jpn) data
        if not check_file(src_data_path):
            return
        with open(src_data_path, "rb") as f:
            data = f.read()
        data = bytearray(data)
        print(f"Data size: {src_data_path}({len(data):,} bytes)")

        # extract scripts
        script, _ = extract_scripts(data, font_table, length_threshold, restriction)

        # save data
        with open(dst_script_path, "w", encoding="utf-8") as f:
            json.dump(script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
