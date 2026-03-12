import os
import sys

sys.path.append("./")
from pathlib import Path
from module.font_table import FontTable
from module.sound import hiragana_pronunciation
from module.jisx0201 import jisx0201_to_unicode


def main():
    os.system("clear")
    font_table_kor = FontTable(Path("font_table/font_table-kor-jin.json"))
    font_table_jpn = FontTable(Path("font_table/font_table-jpn-full.json"))

    # Get a code or codes from a letter or letters
    script = "혓룐"
    sound = ""
    codes_hex = font_table_kor.get_codes(script)

    jpn = ""
    if len(sound):
        for letter in sound:
            ch = hiragana_pronunciation.get(letter)
            if ch is None:
                print(letter)
            else:
                jpn += ch
        print(jpn)

    # 반각 체크
    # halfwidth = "|ﾌ|ﾞ|ﾘ|ﾀ|ｲ|".replace("|", "")
    # halfwidth = halfwidth.encode("cp932")  # 반각 '카타카나 가'
    # print(jisx0201_to_unicode(halfwidth))
    # return

    # codes = "76 57 44 23 61 21 10 0A 11 1B 12 00 20 00 28 13 42 05 21 1D 13 00 00 00 00".replace(" ", "")
    # print(codes)
    # return
    # codes_hex = [codes[i : i + 4] for i in range(0, len(codes), 4)]

    # print(codes_hex)
    hex_str = ""
    hex_str_rev = ""
    for code_hex in codes_hex:
        hex_str_rev += code_hex[2:]  # + " "
        hex_str_rev += code_hex[:2]  # + " "
        hex_str_rev += " "
        hex_str += code_hex
        hex_str += " "

    print(hex_str)
    print(hex_str_rev)

    jpn_script = font_table_jpn.get_chars(codes_hex)
    print(jpn_script + jpn)


if __name__ == "__main__":
    main()
