import os
import json
from pathlib import Path
from module.font_table import FontTable
from module.script import split_sentences


def main():
    platform = "pc98"
    font_table_path = "font_table/font_table-jpn-full.json"
    src_script_path = f"../workspace/script_init-{platform}/EVENT.XOR.DAT_jpn.json"
    dst_script_path = f"../workspace/script-{platform}/EVENT.XOR.DAT_jpn.json"

    # No need to sort since the control codes will be sorted based on the its length
    control_codes = [
        "|W|W|N|X",
        "|W|W|W",
        "|W|W|X",
        "|W|W",
        "|W|N",
        "|W|X",
        "|G|X",
        "|G|N",
        "|N",
    ]
    # control_codes = [
    #     "|W|W|N|X",
    #     "|W|W|W",
    #     "|W|W|X",
    #     "|W|W",
    #     "|W|N",
    #     "|W|X",
    #     "|G|X",
    #     "|G|N",
    #     "|N",
    # ]
    # =================================================================

    font_table = FontTable(font_table_path)
    with open(src_script_path, "r", encoding="utf-8") as f:
        src_script = json.load(f)

    # Split sentences based on the control codes
    sorted_control_codes = sorted(control_codes, key=len, reverse=True)
    script = split_sentences(src_script, font_table, sorted_control_codes)
    script = dict(sorted(script.items()))

    # Save the extracted script to a file in the script directory
    with open(dst_script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
