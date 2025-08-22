import json
from pathlib import Path
from module.font_table import FontTable


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")
    script_dir = base_dir / "script"
    data_dir = base_dir / "m4_jpn"

    font_table = FontTable("./font_table/font_table-jpn.json")
    font_table_5k = FontTable("./font_table/font_table-jpn-5k.json")
    font_table_7k = FontTable("./font_table/font_table-jpn-7k.json")
    font_table_full = FontTable("./font_table/font_table-jpn-full.json")

    # read a pair of scripts
    for file in script_dir.glob("*.json"):  # Use rglob to search subdirectories
        if "_jpn.json" not in file.name:
            continue

        # Read a script
        with open(file, "r", encoding="utf-8") as f:
            script = json.load(f)

        # Read a data file
        data_path = data_dir / file.name.replace("_jpn.json", "")
        assert data_path.exists()
        with open(data_path, "rb") as f:
            data = f.read()
            data = bytearray(data)

        for address, src_sentence in script.items():
            # Ignore the case where the character is in the middle of a sentence
            if "|" in src_sentence:
                continue

            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)

            dst_sentence = ""

            for letter_idx, letter in enumerate(src_sentence):
                pos = letter_idx * 2 + spos
                code_int = (data[pos] << 8) + data[pos + 1]
                code_hex = f"{code_int:X}"
                read_letter = font_table_full.get_char(code_hex)

                if read_letter is None:
                    read_letter = "@"
                    print(1)
                dst_sentence += read_letter

            script[address] = dst_sentence

        print(file)
        with open(file, "w", encoding="utf-8") as f:
            json.dump(script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
