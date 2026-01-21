from module.name_db import NameDB


def main_half():
    name_db = NameDB()
    game = "nb4"

    base_dir = "c:/work_han/workspace3/ss.txt"
    with open(base_dir, "r", encoding="utf-8") as f:
        lines = f.readlines()

    family_name_jpn = ""
    family_name_kor = ""
    given_name_jpn = ""
    given_name_kor = ""

    for line in lines:
        line = line.strip()

        jpn, kor = line.split(":")
        jpn = jpn.strip()
        kor = kor.strip()

        if family_name_jpn == "":
            family_name_jpn = jpn
            family_name_kor = kor
            continue

        given_name_jpn = jpn
        given_name_kor = kor

        full_name_jpn = f"{family_name_jpn} {given_name_jpn}"
        full_name_kor = f"{family_name_kor} {given_name_kor}"

        if name_db.check_full_name_exist(full_name_jpn):
            print(full_name_jpn)
            if full_name_kor != name_db.full_name_db[full_name_jpn]["kor"]:
                print(full_name_kor, name_db.full_name_db[full_name_jpn]["kor"])
        if name_db.check_family_name_exist(family_name_jpn):
            print(family_name_jpn)
            if family_name_kor not in name_db.family_name_db[family_name_jpn]:
                print(family_name_kor, name_db.family_name_db[family_name_jpn])
        if name_db.check_given_name_exist(given_name_jpn):
            print(given_name_jpn)
            if given_name_kor not in name_db.given_name_db[given_name_jpn]:
                print(given_name_kor, name_db.given_name_db[given_name_jpn])

        name_db.add_full_name(full_name_jpn, full_name_kor, game)

        family_name_jpn = ""
        given_name_jpn = ""

    # name_db.save_db()


def main_full():
    name_db = NameDB()
    game = "nb3"

    base_dir = "c:/work_han/workspace3/ss.txt"
    with open(base_dir, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        jpn, kor = line.split("-")
        full_name_jpn = jpn.strip()
        full_name_kor = kor.strip()

        family_name_jpn, given_name_jpn = full_name_jpn.split(" ")
        family_name_kor, given_name_kor = full_name_kor.split(" ")
        if name_db.check_full_name_exist(full_name_jpn):
            print(full_name_jpn)
            if full_name_kor != name_db.full_name_db[full_name_jpn]["kor"]:
                print(full_name_kor, name_db.full_name_db[full_name_jpn]["kor"])
        if name_db.check_family_name_exist(family_name_jpn):
            print(family_name_jpn)
            if family_name_kor not in name_db.family_name_db[family_name_jpn]:
                print(family_name_kor, name_db.family_name_db[family_name_jpn])
        if name_db.check_given_name_exist(given_name_jpn):
            print(given_name_jpn)
            if given_name_kor not in name_db.given_name_db[given_name_jpn]:
                print(given_name_kor, name_db.given_name_db[given_name_jpn])

        name_db.add_full_name(full_name_jpn, full_name_kor, game)

        family_name_jpn = ""
        given_name_jpn = ""

    # name_db.save_db()


if __name__ == "__main__":
    # main_half()
    main_full()
