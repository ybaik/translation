import json
from module.font_table import check_file, FontTable
from module.script import extract_scripts


def main():

    # read a config file
    config_path = "config.json"
    if not check_file(config_path):
        return
    with open(config_path) as f:
        config = json.load(f)

    # read data paths
    src_data_path = config["src_data_file"]
    src_font_table_path = config["src_font_table_file"]
    src_script_path = config["src_script_file"]

    # read a threshold
    length_threshold = config["length_threshold"]

    # read a font table
    if not check_file(src_font_table_path):
        return
    font_table = FontTable(src_font_table_path)

    # read the target (jpn) data
    if not check_file(src_data_path):
        return
    with open(src_data_path, "rb") as f:
        data = f.read()
    print(f"Data size: {src_data_path}({len(data):,} bytes)")

    # extract scripts
    script, script_log = extract_scripts(data, font_table, length_threshold)

    # save the extracted scripts
    with open(src_script_path, "w") as f:
        json.dump(script, f, ensure_ascii=False, indent=4)

    # save logs
    with open("script_log.json", "w") as f:
        json.dump(script_log, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
