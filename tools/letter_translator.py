import sys

sys.path.append("./")
from module.font_table import FontTable

import unicodedata


def jisx0201_to_unicode(
    data: bytes, encoding: str = "cp932", normalize_fullwidth: bool = True, roman_yen: bool = False
) -> str:
    """
    JIS X 0201/Shift_JIS(cp932) 바이트를 유니코드 문자열로 디코딩하고,
    필요 시 반각 가타카나를 전각으로 정규화(NFKC)합니다.

    Parameters
    ----------
    data : bytes
        JIS X 0201/Shift_JIS(cp932) 인코딩된 바이트열.
    encoding : str
        디코딩에 사용할 인코딩 (기본: 'cp932' 또는 'shift_jis').
    normalize_fullwidth : bool
        True면 반각 가타카나(FF61–FF9F)를 전각 가타카나로 변환(NFKC).
    roman_yen : bool
        True면 로마문 0x5C가 백슬래시로 들어온 경우를 '¥'(U+00A5)로 교체.

    Returns
    -------
    str
        유니코드 문자열 (필요 시 전각으로 정규화됨).
    """
    # 1) 디코딩 (JIS X 0201을 포함한 Shift_JIS 계열 권장)
    text = data.decode(encoding, errors="strict")

    # 2) 반각 가타카나 → 전각 가타카나 (및 기타 호환 문자의 표준화)
    if normalize_fullwidth:
        text = unicodedata.normalize("NFKC", text)

    # 3) 로마문 영역의 0x5C(백슬래시) 처리: JIS X 0201에서는 '¥'로 쓰이기도 함
    if roman_yen:
        text = text.replace("\\", "¥")

    return text


def main():
    font_table_kor = FontTable("font_table/font_table-kor-jin.json")
    font_table_jpn = FontTable("font_table/font_table-jpn-full.json")

    # Get a code or codes from a letter or letters
    script = "꽥"  # 籠城
    codes_hex = font_table_kor.get_codes(script)

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
    print(jpn_script)


if __name__ == "__main__":
    main()
