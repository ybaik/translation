import os
import json
import sys

sys.path.append("./")
from module.font_table import FontTable


def main():

    # base_path = '../workspace/Macross3-JPN'
    base_path = "../workspace/Macross3_final"
    path_list = os.listdir(base_path)

    font_table_path = "font_table/anex86kor.json"
    font_table = FontTable(font_table_path)

    sentence_to_find = "쫓"
    address_to_find_hex = font_table.get_codes(sentence_to_find)

    address_to_find_int = []
    for code_hex in address_to_find_hex:
        address_to_find_int.append(int(code_hex, 16))

    for file in path_list:
        target_path = f"{base_path}/{file}"
        if not os.path.isfile(target_path):
            continue

        # read json script
        print(file)
        with open(f"{base_path}/{file}", "rb") as f:
            data = f.read()

        i = 0
        count = 0
        while i < len(data) - 1 - (len(address_to_find_int) - 1) * 2:

            found = True
            for j in range(len(address_to_find_int)):
                idx = j * 2
                # extract a 2byte code
                code_int = (data[i + idx] << 8) + data[i + idx + 1]

                if address_to_find_int[j] != code_int:
                    found = False
                    break
            if found:
                count += 1
                print(f"found a candidate file: {file}:{count}")

            i += 1


if __name__ == "__main__":
    main()
