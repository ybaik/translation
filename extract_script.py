import json
from pathlib import Path
from module.font_table import FontTable
from module.script import extract_script


def main():
    # Read a config file
    config_path = "config.json"
    if not Path(config_path).exists():
        return
    with open(config_path) as f:
        config = json.load(f)

    # Read data paths in the config file
    src_data_path = config["src_data_file"]
    src_font_table_path = config["src_font_table_file"]
    src_script_path = config["src_script_file"]

    # Read a threshold
    length_threshold = config["length_threshold"]
    restriction = config["restriction"]

    # Read a font table
    font_table = FontTable(src_font_table_path)

    # Read the target bianry data
    if not Path(src_data_path).exists():
        return
    with open(src_data_path, "rb") as f:
        data = f.read()
    print(f"Data size: {src_data_path}({len(data):,} bytes)")

    # Extract a script from the binary data
    script, script_log = extract_script(data, font_table, length_threshold, restriction)

    # Save the extracted script to a file in the script directory
    with open(src_script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=4)

    # Save a log file
    with open("script_log.json", "w", encoding="utf-8") as f:
        json.dump(script_log, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
