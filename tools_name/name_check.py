import json
from pathlib import Path
from module.name_db import NameDB
from module.script import Script


def main():
    name_db = NameDB()
    game = "노부나가의 야망 4"
    # print(len(name_db.full_name_db.keys()))
    base_dir = "c:/work_han/workspace3/script-pc98"
    script_jpn = Script(f"{base_dir}/SNDATA2T.CIM_jpn.json")
    script_kor = Script(f"{base_dir}/SNDATA2T.CIM_kor.json")
    # script_jpn = Script(f"{base_dir}/MAIN.EXE_jpn.json")
    # script_kor = Script(f"{base_dir}/MAIN.EXE_kor.json")

    # query = {"game": [game]}
    # print(f"{name_db.check_number(query)} - 노부나가의 야망 4")
    # query = {"game": ["태합입지전 2"]}
    # print(f"{name_db.check_number(query)} - 태합입지전 2")
    # query = {"game": [game, "태합입지전 2"]}
    # print(f"{name_db.check_number(query)} - 태합입지전 2 & 노부나가의 야망 4")
    # print(f"{name_db.check_number()} - Total")
    # name_db.print_duplicate()
    # return

    family_name_jpn = ""
    family_name_kor = ""
    given_name_jpn = ""
    given_name_kor = ""
    prev_address = ""

    mod_list = []

    for address, sentence in script_jpn.script.items():
        start, end = address.split("=")
        start = int(start, 16)
        end = int(end, 16)
        # if start < 0x1192:
        #     continue

        # if start < 0x3F964:
        #     continue
        # if start > 0x41984:
        #     continue

        if len(family_name_jpn) == 0:
            family_name_jpn = sentence
            family_name_kor = script_kor.script[address]
            prev_address = address
            continue

        if len(given_name_jpn) == 0:
            given_name_jpn = sentence
            given_name_kor = script_kor.script[address]

        family_name_jpn = family_name_jpn.replace("␀", "")
        given_name_jpn = given_name_jpn.replace("␀", "")

        full_name_jpn_clean = f"{family_name_jpn} {given_name_jpn}"

        if not name_db.check_full_name_exist(full_name_jpn_clean):
            fn_kor = name_db.family_name_db.get(family_name_jpn, "?")
            gn_kor = name_db.given_name_db.get(given_name_jpn, "?")

            print(f"{full_name_jpn_clean} - {fn_kor} {gn_kor} - is not in the name database.")

            _, prior = prev_address.split("=")
            post, _ = address.split("=")
            prior = int(prior, 16)
            post = int(post, 16)
            if post - prior > 6:
                print(f"Address mismatch: {prev_address}:{post - prior}")
                break
            family_name_jpn = ""
            given_name_jpn = ""
            continue
        else:
            if game not in name_db.full_name_db[full_name_jpn_clean]["game"]:
                print(full_name_jpn_clean)
                name_db.full_name_db[full_name_jpn_clean]["game"].append(game)

        # Check
        if given_name_jpn == given_name_kor:
            name_full_kor = name_db.full_name_db[full_name_jpn_clean]["kor"]
            name_kor = name_full_kor.split(" ")[-1]
            if len(name_kor) < 4:
                info_str = f"{address},{given_name_jpn},{name_kor}"
                mod_list.append(info_str)
                print(info_str)

        if family_name_jpn == family_name_kor:
            name_kor = name_db.full_name_db[full_name_jpn_clean]["kor"].split(" ")[0]
            if len(name_kor) < 4:
                info_str = f"{prev_address},{family_name_jpn},{name_kor}"
                mod_list.append(info_str)
                print(info_str)

        family_name_jpn = ""
        given_name_jpn = ""

    name_db.save_db()
    # return
    for info_str in mod_list:
        address, jpn, kor = info_str.split(",")

        start, end = address.split("=")
        start = int(start, 16)
        end = int(end, 16)

        diff = len(kor) - len(jpn)

        if diff > 0:
            end += diff * 2
            jpn += "␀" * diff

        script_jpn.replace_sentence(address, f"{start:05X}={end:05X}", jpn)
        script_kor.replace_sentence(address, f"{start:05X}={end:05X}", kor)

    # script_jpn.save(f"{base_dir}/SNDATA2T.CIM_jpn.json")
    # script_kor.save(f"{base_dir}/SNDATA2T.CIM_kor.json")
    # script_jpn.save(f"{base_dir}/MAIN.EXE_jpn.json")
    # script_kor.save(f"{base_dir}/MAIN.EXE_kor.json")

    # name_db.save_db()


if __name__ == "__main__":
    main()
