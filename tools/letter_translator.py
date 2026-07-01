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
    font_table_jpn = FontTable(Path("font_table/font_table-jpn.json"))

    # Get a code or codes from a letter or letters
    script = "오다"
    sound = ""
    codes_hex = font_table_kor.get_codes(script)
    # codes_hex = font_table_jpn.get_codes(script)
    print(codes_hex)

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

    hex_str = ""
    hex_str_rev = ""
    for code_hex in codes_hex:
        hex_str_rev += code_hex[2:]  # + " "
        hex_str_rev += code_hex[:2]  # + " "
        hex_str_rev += " "
        hex_str += code_hex
        hex_str += " "

    print(hex_str)
    # print(hex_str_rev)

    jpn_script = font_table_jpn.get_chars(codes_hex)
    # jpn_script = font_table_kor.get_chars(codes_hex)
    print(jpn_script + jpn)


if __name__ == "__main__":
    main()
