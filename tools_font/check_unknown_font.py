import json
from pathlib import Path
from module.font_table import check_file, FontTable


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")
    bin_dir = base_dir / "m2_dos"
    font_table = FontTable(base_dir / "anex86dos_m2.tbl")

    # read a pair of scripts
    # for file in base_dir.glob("*.json"): # Use rglob to search subdirectories

    cnt = 0
    code_set = set()

    for file in bin_dir.glob("*.bin"):

        json_path = base_dir / f"{file.stem}_dos.json"
        if not json_path.exists():
            continue
        with open(json_path, "r") as f:
            src = json.load(f)

        data = None

        is_updated = False

        # check address
        for address, src_dialogue in src.items():
            if "@" not in src_dialogue:
                continue

            cnt += 1

            # print(src_dialogue)
            if data == None:
                with open(file, "rb") as f:
                    data = f.read()

            # Find the position of "@" in the string
            at_index = src_dialogue.find("@")

            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            pos = spos + at_index * 2

            code_int = (data[pos] << 8) + data[pos + 1]
            code_hex = f"{code_int:X}"

            character = font_table.get_char(code_hex)
            if character is None:
                # print(json_path.name)
                # print(code_hex)
                # print(src_dialogue)
                code_set.add(code_hex)
            else:
                src_dialogue = list(src_dialogue)
                src_dialogue[at_index] = character
                src_dialogue = "".join(src_dialogue)
                src[address] = src_dialogue
                is_updated = True

        if is_updated:
            with open(json_path, "w") as f:
                json.dump(src, f, ensure_ascii=False, indent=4)

    code_set = list(code_set)
    code_set.sort()
    print(code_set)
    print(cnt)


if __name__ == "__main__":
    main()
