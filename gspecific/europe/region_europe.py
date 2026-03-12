import json
from pathlib import Path
from module.jisx0201 import jisx0201_to_unicode
from module.font_table import FontTable

input = {
    "0DF68=0DF70": "|ｽ|ﾄ|ﾗ|ｽ|ﾌ|ﾞ|ﾙ|ｸ|ﾞ",
    "0DFA2=0DFAA": "|F|ｽ|ﾃ|ﾝ|ﾊ|ﾞ|ﾙ|ﾄ|ﾞ",
    "0DFDC=0DFE0": "|ﾍ|ﾞ|ｽ|ｺ|ﾌ",
    "0E016=0E01A": "|ﾚ|ｯ|ﾁ|ｪ|ﾝ",
    "0E050=0E053": "|ｾ|ｰ|ﾛ|ﾌ",
    "0E08A=0E08E": "|ﾚ|ｰ|ﾊ|ﾞ|ｽ",
    "0E0C4=0E0CA": "|ﾌ|ﾗ|ﾝ|ｸ|ﾌ|ﾙ|ﾄ",
    "0E0FE=0E104": "|ﾐ|ｭ|ﾙ|ﾛ|ｰ|ｾ|ﾞ",
    "0E138=0E13D": "|ｷ|ｭ|ｽ|ﾄ|ﾘ|ﾝ",
    "0E172=0E17B": "|E|ﾋ|ｭ|ｯ|ﾃ|ﾝ|ｽ|ﾀ|ｯ|ﾄ",
    "0E1AC=0E1B5": "|ｽ|ﾞ|ｨ|ｰ|ﾋ|ﾞ|ﾝ|ｹ|ﾞ|ﾝ",
    "0E1E6=0E1EB": "|ｳ|ﾞ|ｨ|ｴ|ｯ|ﾂ",
    "0E220=0E225": "|ﾄ|ﾞ|ﾛ|ｯ|ｾ|ﾝ",
    "0E25A=0E25E": "|ﾚ|ｯ|ﾍ|ﾟ|ﾝ",
}


def main():
    base_dir = Path("./gspecific/europe")
    json_path = base_dir / "europe_region.json"
    with open(json_path, "r", encoding="utf-8") as f:
        europe_region = json.load(f)

    font_table_path = Path("font_table/font_table-kor-jin.json")
    kor_font_table = FontTable(font_table_path)

    is_updated = False
    # for i, (k, v) in enumerate(input.items()):
    #     exists = False
    #     for k_db, v_db in europe_region.items():
    #         if v_db["jpn_org"] == v:
    #             exists = True
    #             break
    #     if exists:
    #         continue
    #     is_updated = True
    #     europe_region[f"unknown{i:02d}"] = {
    #         "jpn_org": v,
    #         "jpn": jisx0201_to_unicode(v.replace("|", "").encode("cp932")),
    #         "kor": "",
    #     }

    count = 1
    for k, v in europe_region.items():
        if "kor" not in v:
            continue
        kor = v.get("kor")

        length = kor_font_table.check_length_from_sentence(kor)
        if length <= 10:
            continue

        print(count, k, v.get("jpn"), kor)
        count += 1

    # is_updated = True

    if is_updated:
        sorted_dict = dict(sorted(europe_region.items(), key=lambda item: item[0]))
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(sorted_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
