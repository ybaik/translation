import os
import json
from pathlib import Path
from module.font_table import check_file, FontTable
from module.script import extract_script


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
        # Read a font table
        if not check_file(font_table_path):
            return
        font_table = FontTable(font_table_path)

        # Read a target binary data
        if not check_file(src_data_path):
            return
        with open(src_data_path, "rb") as f:
            data = f.read()
        data = bytearray(data)
        print(f"Data size: {src_data_path}({len(data):,} bytes)")

        # Extract a script from the binary data
        script, _ = extract_script(data, font_table, length_threshold, restriction)

        # Save the extracted script to a file in the script directory
        with open(dst_script_path, "w", encoding="utf-8") as f:
            json.dump(script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
