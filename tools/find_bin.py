import sys
from pathlib import Path

sys.path.append("./")
from module.font_table import FontTable
from module.decoding import decode


def main():
    ws_num = 5
    base_path = Path(f"../workspace{ws_num}/jpn-pc98")

    check_xor = True

    # font_table_path = "font_table/font_table-kor-jin.json"
    font_table_path = Path("font_table/font_table-jpn-full.json")
    font_table = FontTable(font_table_path)

    sentence_to_find = "出現"
    address_to_find_hex = font_table.get_codes(sentence_to_find)

    print(address_to_find_hex)
    code_string_hex = ""
    for code_hex in address_to_find_hex:
        code_hex = code_hex.replace("0x", "")
        code_string_hex += code_hex

    # code_string_hex = "CAB5B3"
    size_byte = len(code_string_hex) // 2
    code_array_int = []
    for i in range(size_byte):
        code_int = int(code_string_hex[i * 2 : i * 2 + 2], 16)
        code_array_int.append(code_int)

    for file in base_path.rglob("*.*"):  # Use rglob to search subdirectories
        if not file.is_file():
            continue
        print(file.name)
        # if "MAIN" not in file:
        #     continue

        if "M" not in file.name:
            continue

        if check_xor:
            for dc in range(0, 0xFF):
                decoding_info = f"xor:0x{dc:02X}"
                # Read a json script
                # print(file)
                with open(file, "rb") as f:
                    data = f.read()
                data = decode(data, decoding_info)

                i = 0
                count = 0
                while i < len(data) - 1 - size_byte:
                    found = True
                    for j in range(size_byte):
                        # Extract a 2byte code
                        code_int = data[i + j]

                        if code_array_int[j] != code_int:
                            found = False
                            break
                    if found:
                        count += 1
                        print(f"found a candidate file: {i:X} - {file}:{count}, xor:{dc:02X}")
                    i += 1
        else:
            with open(file, "rb") as f:
                data = f.read()
            i = 0
            count = 0
            while i < len(data) - 1 - size_byte:
                found = True
                for j in range(size_byte):
                    # Extract a 2byte code
                    code_int = data[i + j]

                    if code_array_int[j] != code_int:
                        found = False
                        break
                if found:
                    count += 1
                    print(f"found a candidate file: {i:X} - {file}:{count}")
                i += 1


if __name__ == "__main__":
    main()
