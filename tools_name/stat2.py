from module.name_db import NameDB


def main():
    name_db = NameDB()
    game = "nobu4"
    name_set = set()
    for k, v in name_db.full_name_db.items():
        if game not in v["game"]:
            continue
        kn = v.get("kor")
        if kn is None:
            assert 0, f"kor is None: {k}"

        fn, gn = kn.split(" ")
        if len(fn) == 4:
            name_set.add(fn)
        if len(gn) == 4:
            name_set.add(gn)

    for i, name in enumerate(name_set, start=1):
        print(f"{i:02d} - {name}")


if __name__ == "__main__":
    main()
