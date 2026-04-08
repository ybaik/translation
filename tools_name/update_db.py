import json
from pathlib import Path


def main():
    game = "taiko1"
    db_json_path = Path("./name_db/item_db.json")
    with open(db_json_path, "r", encoding="utf-8") as f:
        db_json = json.load(f)

    # Read contents
    # jpn_script_path = Path("../workspace1/script-pc98/TITEM.DAT_jpn.json")
    # kor_script_path = Path("../workspace1/script-pc98/TITEM.DAT_kor.json")
    jpn_script_path = Path("../workspace1/script-pc98/MAIN.EXE_jpn.json")
    kor_script_path = Path("../workspace1/script-pc98/MAIN.EXE_kor.json")
    with open(jpn_script_path, "r", encoding="utf-8") as f:
        jpn_script = json.load(f)
    with open(kor_script_path, "r", encoding="utf-8") as f:
        kor_script = json.load(f)

    for address, sentence in jpn_script.items():
        if "=" not in address:
            continue
        start, end = address.split("=")
        start = int(start, 16)
        end = int(end, 16)

        # if start < 0x41C6F:
        #     continue
        if start > 0x56102:
            continue

        sentence = sentence.replace("|␀", "")
        sentence = sentence.replace("␀", "")
        kor_sentence = kor_script[address]
        kor_sentence = kor_sentence.replace("|␀", "")
        kor_sentence = kor_sentence.replace("␀", "")

        if sentence not in db_json:
            continue

        # if sentence not in db_json:
        #     db_json[sentence] = {
        #         "kor": kor_sentence,
        #         "game": [game],
        #     }
        #     continue

        # If the item is in the DB
        # if game in db_json[sentence]["game"]:
        #     continue

        # if db_json[sentence]["kor"] == kor_sentence:
        #     db_json[sentence]["game"].append(game)
        #     continue

        if kor_sentence == db_json[sentence]["kor"]:
            print(sentence)
            print(kor_sentence)
            continue

        print(sentence)
        print(kor_sentence)
        print(db_json[sentence]["kor"])
        print(1)

    # with open(db_json_path, "w", encoding="utf-8") as f:
    #     json.dump(db_json, f, ensure_ascii=False, indent=4, sort_keys=True)


if __name__ == "__main__":
    main()
