import sys
from pathlib import Path

sys.path.append("./")
from module.font_table import FontTable


def main():
    # Read a font table
    font_table_jpn = FontTable(Path("font_table/font_table-jpn-full.json"))
    # font_table_kor = FontTable(Path("font_table/font_table-kor-jin.json"))

    # Get a letter or letters from a code or codes
    code_txt = "8E 9E EB EE"
    code_list = code_txt.split(" ")
    codes = [f"{code_list[i]}{code_list[i + 1]}" for i in range(0, len(code_list), 2)]
    word = font_table_jpn.get_chars(codes)
    # word = font_table_kor.get_chars(codes)
    print(word)


if __name__ == "__main__":
    main()
