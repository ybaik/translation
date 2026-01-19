from module.name_db import NameDB
from module.script import Script
from rich.console import Console


def main():
    console = Console()
    name_db = NameDB()
    game = "nobu4"
    base_dir = "c:/work_han/workspace3/script-pc98"

    file_name = "SNDATA3T.CIM"
    script_jpn = Script(f"{base_dir}/{file_name}_jpn.json")
    script_kor = Script(f"{base_dir}/{file_name}_kor.json")

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

        if "0x:" in family_name_jpn:
            family_name_jpn = name_db.get_name_from_code("family", family_name_jpn, game)
        if "0x:" in given_name_jpn:
            given_name_jpn = name_db.get_name_from_code("given", given_name_jpn, game)

        full_name_jpn_clean = f"{family_name_jpn} {given_name_jpn}"

        if not name_db.check_full_name_exist(full_name_jpn_clean):
            db = name_db.family_name_db.get(family_name_jpn)
            fn_kor = "?" if db is None else db.get("kor", "?")
            db = name_db.given_name_db.get(given_name_jpn)
            gn_kor = "?" if db is None else db.get("kor", "?")

            console.print(f"{full_name_jpn_clean} - {fn_kor} {gn_kor}")
            if fn_kor == "?":
                kor = name_db.given_name_db.get(family_name_jpn, "?")
                if kor != "?":
                    console.print("Warning: Family name is in the given name database.")
            if gn_kor == "?":
                kor = name_db.family_name_db.get(given_name_jpn, "?")
                if kor != "?":
                    console.print("Warning: Given name is in the family name database.")

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

    # script_jpn.save(f"{base_dir}/{file_name}_jpn.json")
    # script_kor.save(f"{base_dir}/{file_name}_kor.json")
    # name_db.save_db()


if __name__ == "__main__":
    main()
