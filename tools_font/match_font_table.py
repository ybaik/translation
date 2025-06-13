import json
from pathlib import Path


def main():
    base_path = Path("./font_table/")

    src_path = Path("./data") / "shiftjis.json"

    # src_path = base_path / "font_table-jpn-60K.json"
    dst_path = base_path / "font_table-jpn-full.json"

    with open(src_path, "r", encoding="utf-8") as f:
        src_font_table = json.load(f)

    with open(dst_path, "r", encoding="utf-8") as f:
        dst_font_table = json.load(f)

    for key, src_value in src_font_table.items():
        src_code = int(key, 16)
        # if src_code < int("889F", 16):
        #     continue
        # if src_code < int ("9FFC", 16):
        #     continue
        if src_code > int("EAA4", 16):
            continue

        # if src_code > int ("9872", 16):
        #     continue
        # if src_code > int ("9FFC", 16):
        #     continue
        if src_code > int("EAA4", 16):
            continue

        dst_value = dst_font_table[key]

        if dst_value != src_value:
            dst_font_table[key] = src_value

    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(dst_font_table, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
