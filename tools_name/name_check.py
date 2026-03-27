from module.name_db import NameDB
from module.script import Script
from rich.console import Console


def main():
    console = Console()
    name_db = NameDB()
    game = "taiko2"
    ws_num = 2
    base_dir = f"c:/work_han/workspace{ws_num}/script-pc98"

    file_name = "BSDATA1.TR2"
    # file_name = "MAIN.EXE"
    script_jpn = Script(f"{base_dir}/{file_name}_jpn.json")
    script_kor = Script(f"{base_dir}/{file_name}_kor.json")

    fn_jpn = ""
    gn_jpn = ""
    prev_address = ""

    for address, sentence in script_jpn.script.items():
        start, end = address.split("=")
        start = int(start, 16)
        end = int(end, 16)

        if game == "taiko1":
            if file_name == "MAIN.EXE":
                if start < 0x5671C:
                    continue
                if start > 0x5A9B3:
                    continue
        # else:
        #     continue
        if start < 0x8698:
            continue

        if len(fn_jpn) == 0:
            fn_jpn = sentence
            prev_address = address
            continue

        if len(gn_jpn) == 0:
            gn_jpn = sentence

        fn_jpn = fn_jpn.replace("␀", "")
        gn_jpn = gn_jpn.replace("␀", "")

        if "0x:" in fn_jpn:
            fn_jpn = name_db.get_name_from_code("family", fn_jpn, game)
        if "0x:" in gn_jpn:
            gn_jpn = name_db.get_name_from_code("given", gn_jpn, game)

        full_name_jpn_clean = f"{fn_jpn} {gn_jpn}"

        if not name_db.check_full_name_exist(full_name_jpn_clean):
            db = name_db.family_name_db.get(fn_jpn)
            db_fn_kor = "?" if db is None else db.get("kor", "?")
            db = name_db.given_name_db.get(gn_jpn)
            db_gn_kor = "?" if db is None else db.get("kor", "?")

            console.print(f"{full_name_jpn_clean} - {db_fn_kor} {db_gn_kor}")

            if db_fn_kor == "?":
                kor = name_db.given_name_db.get(fn_jpn, "?")
                if kor != "?":
                    console.print("Warning: Family name is in the given name database.")
            if db_gn_kor == "?":
                kor = name_db.family_name_db.get(gn_jpn, "?")
                if kor != "?":
                    console.print("Warning: Given name is in the family name database.")

            _, prior = prev_address.split("=")
            post, _ = address.split("=")
            prior = int(prior, 16)
            post = int(post, 16)
            if post - prior > 8:
                print(f"Address mismatch: {prev_address}:{post - prior}")
                break
            fn_jpn = ""
            gn_jpn = ""
            continue
        else:
            if game not in name_db.full_name_db[full_name_jpn_clean]["game"]:
                print(full_name_jpn_clean)
                name_db.full_name_db[full_name_jpn_clean]["game"].append(game)

        db_fn_kor, db_gn_kor = name_db.full_name_db[full_name_jpn_clean]["kor"].split(" ")
        fn_jpn = ""
        gn_jpn = ""

    # for info_str in mod_list:
    #     address, jpn, kor = info_str.split(",")

    #     start, end = address.split("=")
    #     start = int(start, 16)
    #     end = int(end, 16)

    #     diff = len(kor) - len(jpn)

    #     if diff > 0:
    #         end += diff * 2
    #         jpn += "␀" * diff

    #     script_jpn.replace_sentence(address, f"{start:05X}={end:05X}", jpn)
    #     script_kor.replace_sentence(address, f"{start:05X}={end:05X}", kor)

    # script_jpn.save(f"{base_dir}/{file_name}_jpn.json")
    # script_kor.save(f"{base_dir}/{file_name}_kor.json")
    # name_db.save_db()


if __name__ == "__main__":
    main()
