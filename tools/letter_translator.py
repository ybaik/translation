import sys

sys.path.append("./")
from module.font_table import FontTable


def main():
    font_table_kor = FontTable("font_table/font_table-kor-jin.json")
    font_table_jpn = FontTable("font_table/font_table-jpn-full.json")

    # Get a code or codes from a letter or letters
    script = "꼍텐"
    codes_hex = font_table_kor.get_codes(script)

    # codes = "76 57 44 23 61 21 10 0A 11 1B 12 00 20 00 28 13 42 05 21 1D 13 00 00 00 00".replace(" ", "")
    # print(codes)
    # return
    # codes_hex = [codes[i : i + 4] for i in range(0, len(codes), 4)]

    # print(codes_hex)

    hex_str = ""
    for code_hex in codes_hex:
        hex_str += code_hex[2:]  # + " "
        hex_str += code_hex[:2]  # + " "
        hex_str += " "
    print(hex_str)

    jpn_script = font_table_jpn.get_chars(codes_hex)
    print(jpn_script)


if __name__ == "__main__":
    main()
