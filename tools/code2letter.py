import os
import sys

sys.path.append("./")
from module.font_table import FontTable


def main():

    # read font table
    font_table = FontTable("font_table/font_table-kor-jin.json")

    # code to letter
    codes = ["88d7", "94ca"]
    letter = font_table.get_char(codes[0].upper())
    word = font_table.get_chars(codes)
    print(letter, word)

    # letter to code
    script = "쫓구"
    code_hex = font_table.get_code("_")
    codes_hex = font_table.get_codes(script)

    print(code_hex)
    print(codes_hex)


if __name__ == "__main__":
    main()
