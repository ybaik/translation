import sys
from pathlib import Path

sys.path.append("./")
from module.font_table import FontTable


def main():
    # Read a font table
    font_table_jpn = FontTable(Path("font_table/font_table-jpn-full.json"))
    font_table_kor = FontTable(Path("font_table/font_table-kor-jin.json"))

    # Get a letter or letters from a code or codes
    code_txt = "88 DA 93 AE"
    code_list = code_txt.split(" ")
    codes = [f"{code_list[i]}{code_list[i + 1]}" for i in range(0, len(code_list), 2)]
    # letter = font_table_jpn.get_char(codes[0].upper())
    word = font_table_jpn.get_chars(codes)
    print(word)


if __name__ == "__main__":
    main()
