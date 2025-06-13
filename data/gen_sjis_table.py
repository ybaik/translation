import json
from pathlib import Path


def main():
    sjis_path = Path("./data/shiftjis.txt")
    with open(sjis_path, "r", encoding="utf-8") as f:
        sjis = f.readlines()

    table = dict()

    for line_idx, line in enumerate(sjis):
        if line_idx < 2:
            continue

        start_code = line[2:7].replace(" ", "").upper()
        data = line[10:]
        # print(start_code)

        idx = 0
        letter_count = 0
        start_code_int = int(start_code, 16)
        while idx < len(data):
            letter = "unknown"
            if data[idx] == " " and data[idx + 1] == " ":
                letter = "space"
                idx += 2
            else:
                next = data[idx:].find(" ")

                if next == -1:
                    break
                letter = data[idx : idx + next]
                idx += next

            new_code_int = start_code_int + letter_count
            new_code_hex = f"{new_code_int:X}"
            # print(f"{new_code_hex}={letter}"

            if letter not in ["unknown", "space"]:
                if new_code_hex not in table:
                    table[new_code_hex] = letter

            letter_count += 1
            idx += 1

    with open("./data/shiftjis.json", "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
