import os
import json
import sys

sys.path.append("./")
from module.font_table import FontTable
from module.decoding import decode


def main():
    base_path = "../workspace/jpn-dos"
    path_list = os.listdir(base_path)

    # font_table_path = "font_table/font_table-kor-jin.json"
    font_table_path = "font_table/font_table-jpn-full.json"
    font_table = FontTable(font_table_path)

    sentence_to_find = "達"
    address_to_find_hex = font_table.get_codes(sentence_to_find)

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

    for file in path_list:
        target_path = f"{base_path}/{file}"
        if not os.path.isfile(target_path):
            continue

        if "MAIN" not in file:
            continue

        # Read a json script
        # print(file)
        with open(f"{base_path}/{file}", "rb") as f:
            data = f.read()

        # decoding_info = "xor:0x77"
        # data = decode(data, decoding_info)

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
