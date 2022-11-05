import json
from module.font_table import check_file, FontTable
from module.script import write_scripts
from check_script import check_script


def main():

    config_path = "config.json"
    if not check_file(config_path):
        return
    with open("config.json") as f:
        config = json.load(f)

    dst_font_table_path = config["dst_font_table_file"]
    dst_script_path = config["dst_script_file"]
    src_data_path = config["src_data_file"]
    dst_data_path = config["dst_data_file"]

    # read scripts
    with open(dst_script_path, "r") as f:
        scripts = json.load(f)

    # read a font table
    if not check_file(dst_font_table_path):
        return
    font_table = FontTable(dst_font_table_path)

    # check scripts
    count_false_length, count_false_letters = check_script(scripts, font_table)
    print(
        f"False sentence length and letter count: {count_false_length}, {count_false_letters}"
    )

    if count_false_length or count_false_letters:
        print("False sentence length or letters should be fixed.")
        return

    # read the target (jpn) data
    if not check_file(src_data_path):
        return
    with open(src_data_path, "rb") as f:
        data = f.read()
    data = bytearray(data)
    print(f"Data size: {src_data_path}({len(data):,} bytes)")

    # write script
    data = write_scripts(data, font_table, scripts)

    # save data
    with open(dst_data_path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
