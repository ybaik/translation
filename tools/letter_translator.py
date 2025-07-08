import os
import sys

sys.path.append("./")
from module.font_table import FontTable


def main():

    font_table_kor = FontTable("font_table/font_table-kor-jin.json")
    font_table_jpn = FontTable("font_table/font_table-jpn-full.json")

    # Get a code or codes from a letter or letters
    script = "쇠씹"
    codes_hex = font_table_kor.get_codes(script)
    jpn_script = font_table_jpn.get_chars(codes_hex)
    print(jpn_script)


if __name__ == "__main__":
    main()
