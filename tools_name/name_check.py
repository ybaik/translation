import json
from pathlib import Path
from module.name_db import NameDB
from module.script import Script


def main():
    name_db = NameDB()
    game = "노부나가의 야망 4"
    # print(len(name_db.full_name_db.keys()))
    base_dir = "c:/work_han/workspace3/script-pc98"
    script = Script(f"{base_dir}/SNDATA1.CIM_jpn.json")

    print(name_db.check_number())
    query = {"game": "노부나가의 야망 4"}
    print(name_db.check_number(query))

    name_db.print_duplicate()

    return

    family_name = ""
    given_name = ""
    for address, sentence in script.script.items():
        start, end = address.split("=")
        start = int(start, 16)
        end = int(end, 16)
        if start < 0x1192:
            continue

        if len(family_name) == 0:
            family_name = sentence
            continue

        if len(given_name) == 0:
            given_name = sentence

        full_name = f"{family_name} {given_name}"

        if name_db.check_name_exist(full_name):
            games = name_db.full_name_db[full_name]["game"]
            games.append(game)

        family_name = ""
        given_name = ""

    # name_db.save_db()


if __name__ == "__main__":
    main()
