import re
import sys
from pathlib import Path

sys.path.append("./")
from module.font_table import FontTable
from module.decoding import decode


def main():
    ws_num = 5
    base_path = Path(f"../workspace{ws_num}/jpn-pc98-decoded")

    check_xor = False

    # font_table_path = "font_table/font_table-kor-jin.json"
    font_table_path = Path("font_table/font_table-jpn-full.json")
    font_table = FontTable(font_table_path)

    sentence_to_find = "水色"
    address_to_find_hex = font_table.get_codes(sentence_to_find)
    print(address_to_find_hex)
    target_bytes = bytearray.fromhex("".join(address_to_find_hex))

    for file in base_path.rglob("*.*"):  # Use rglob to search subdirectories
        if not file.is_file():
            continue
        print(file.name)
        if "MESS03" not in file.name:
            continue

        with open(file, "rb") as f:
            raw_data = f.read()

        if check_xor:
            for dc in range(0, 0xFF):
                decoding_info = f"xor:0x{dc:02X}"
                # Read a json script
                # print(file)
                data = decode(raw_data, decoding_info)
                position = data.find(target_bytes)

                if position != -1:
                    print(f"found a candidate file: {position:X} - {file}, xor:{dc:02X}")
        else:
            matches = re.finditer(re.escape(target_bytes), raw_data)
            positions = [match.start() for match in matches]
            for position in positions:
                print(f"found a candidate file: 0x{position:X} - {file}")


if __name__ == "__main__":
    main()
