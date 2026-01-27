import os
import json
from pathlib import Path
from module.font_table import FontTable
from module.script import extract_script
from module.decoding import decode


def main():
    workspace = "workspace5"
    platform = "pc98"
    bin_path = f"../{workspace}/jpn-{platform}"
    font_table_path = "font_table/font_table-jpn-full.json"
    extended_word = "_jpn"
    script_init_path = f"../{workspace}/script_init-{platform}"
    script_base_path = f"../{workspace}/script-{platform}"

    # dos kor
    # bin_path = f"../{workspace}/kor-{platform}"
    # font_table_path = f"../{workspace}/font_table-kor-suho.tbl"
    # extended_word = "_kor"
    # script_path = f"../{workspace}/script_init-{platform}"

    length_threshold_in_bytes = 1
    check_ascii = True
    check_ascii_restriction = False  # If True, the first ASCII code needs to be x20

    decoding_info = "xor:0x96"
    decoding_base_path = f"../workspace0/jpn-decoded-{platform}"
    # =================================================================

    files = os.listdir(bin_path)
    # files = os.listdir(ref_dir)

    for file in files:
        src_data_path = f"{bin_path}/{file}"
        dst_script_path = f"{script_init_path}/{file}{extended_word}.json"

        # if "SNDATA3" not in file:
        #     continue

        if not os.path.isfile(src_data_path):
            continue

        print(f"{file} ===========================================")
        # Read a font table
        font_table = FontTable(font_table_path, script_base_path)

        # Read a target binary data
        with open(src_data_path, "rb") as f:
            data = f.read()
        data = bytearray(data)

        # Decoding
        # data = decode(data, decoding_info)
        # decoding_path = f"{decoding_base_path}/{file}"
        # with open(decoding_path, "wb") as f:
        #     f.write(data)

        print(f"Data size: {src_data_path}({len(data):,} bytes)")

        # Extract a script from the binary data
        script, _ = extract_script(
            data=data,
            font_table=font_table,
            length_threshold=length_threshold_in_bytes,
            check_ascii=check_ascii,
            check_ascii_restriction=check_ascii_restriction,
        )

        # Save the extracted script to a file in the script directory
        with open(dst_script_path, "w", encoding="utf-8") as f:
            json.dump(script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
