import json
from pathlib import Path
from module.font_table import FontTable
from module.script import write_script
from module.check_script import check_script


def main():
    config_path = "config.json"
    if not Path(config_path).exists():
        return
    with open("config.json") as f:
        config = json.load(f)

    dst_font_table_path = config["dst_font_table_file"]
    dst_script_path = config["dst_script_file"]
    src_data_path = config["src_data_file"]
    dst_data_path = config["dst_data_file"]

    # Read a script
    with open(dst_script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    # Read a font table
    if not Path(dst_font_table_path).exists():
        return
    font_table = FontTable(dst_font_table_path)

    # Check the script
    count_false_length, count_false_letters = check_script(script, font_table)
    print(f"False sentence length and letter count: {count_false_length}, {count_false_letters}")

    if count_false_length or count_false_letters:
        print("False sentence length or letters should be fixed.")
        return

    # Read the source binary data
    if Path(src_data_path).exists():
        return
    with open(src_data_path, "rb") as f:
        data = f.read()
    data = bytearray(data)
    print(f"Data size: {src_data_path}({len(data):,} bytes)")

    # Write the script to the binary data in memory
    data = write_script(data, font_table, script)

    # Save the replaced binary data to a file in the destination directory
    with open(dst_data_path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
