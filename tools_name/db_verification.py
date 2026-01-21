from module.name_db import NameDB


def main():
    name_db = NameDB()

    for full_name_jpn, info in name_db.full_name_db.items():
        family_name_jpn, given_name_jpn = full_name_jpn.split(" ")
        family_name_kor, given_name_kor = info["kor"].split(" ")

        if "desc" in info:
            family_name_kor, given_name_kor = info["desc"].get("kor_org").split(" ")

        # Check family name
        if family_name_jpn in name_db.family_name_db:
            db = name_db.family_name_db[family_name_jpn]
            db_name_kor = db.get("kor")
            if isinstance(db_name_kor, str):
                if db_name_kor != family_name_kor:
                    print(f"Family name: {full_name_jpn} - {family_name_jpn}:{family_name_kor}")
                    print(db)
            else:
                if family_name_kor not in db_name_kor:
                    print(f"Family name: {full_name_jpn} - {family_name_jpn}:{family_name_kor}")
                    print(db)
        else:
            print(f"No db - Family name: {full_name_jpn} - {family_name_jpn}:{family_name_kor}")
            print(info)

        # Check given name
        if given_name_jpn in name_db.given_name_db:
            db = name_db.given_name_db[given_name_jpn]
            db_name_kor = db.get("kor")
            if isinstance(db_name_kor, str):
                if db_name_kor != given_name_kor:
                    print(f"Given name: {full_name_jpn} - {given_name_jpn}:{given_name_kor}")
                    print(db)
            else:
                if given_name_kor not in db_name_kor:
                    print(f"No db - Given name: {full_name_jpn} - {given_name_jpn}:{given_name_kor}")
                    print(db)


if __name__ == "__main__":
    main()
