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

    name_list = list(name_set)
    name_list.sort()
    for i, name in enumerate(name_list):
        print(f"{i + 1:03d}: {name}")

    return

    with open("c:/work_han/workspace3/names.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    half_name = set()
    for name in name_set:
        half_name.add(name[:2])
        half_name.add(name[2:])

    cc = set()
    for line in lines:
        cc.add(line.strip())
    out = half_name - cc
    print(out)
    out2 = cc - half_name
    print(out2)


if __name__ == "__main__":
    main()
