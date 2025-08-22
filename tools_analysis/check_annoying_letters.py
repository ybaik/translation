import json
from pathlib import Path
from module.font_table import FontTable


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")
    script_dir = base_dir
    data_dir = base_dir / "m4_jpn"
    font_table = FontTable("./font_table/font_table-jpn-40k.json")
    target_letter = "■"  # @"
    # target_letter = "@"

    # read a pair of scripts
    for file in script_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue
        with open(file, "r", encoding="utf-8") as f:
            script = json.load(f)

        data = None
        is_updated = False
        for address, src_sentence in script.items():
            if target_letter not in src_sentence:
                continue

            # Ignore the case where the character is in the middle of a sentence
            if "|" in src_sentence:
                continue

            if data is None:
                data_path = data_dir / file.name.replace("_jpn.json", "")
                # print(data_path)
                assert data_path.exists()

                with open(data_path, "rb") as f:
                    data = f.read()
                    data = bytearray(data)

            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)

            letter_pos = src_sentence.find(target_letter)
            pos = spos + letter_pos * 2

            code_int = (data[pos] << 8) + data[pos + 1]
            code_hex = f"{code_int:X}"
            read_letter = font_table.get_char(code_hex)

            if read_letter is None:
                print(f"Character {code_hex} is none in the font table. {address}, {file}")
            elif read_letter not in ["■", "@"]:
                new_sentence = src_sentence[:letter_pos] + read_letter
                if len(src_sentence) > letter_pos + 1:
                    new_sentence += src_sentence[letter_pos + 1 :]
                script[address] = new_sentence
                is_updated = True
            else:
                print(f"Character {code_hex} is not found in the font table. {address}, {file}")

        if is_updated:
            print(file)
            with open(file, "w", encoding="utf-8") as f:
                json.dump(script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
