from module.name_db import NameDB
from rich.console import Console


def main():
    console = Console()
    name_db = NameDB()
    base_dir = "c:/work_han/workspace3"

    with open(f"{base_dir}/장명.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if "-" in line:
            continue

        # remove explain
        line = line.split("(")[0]
        jpn, kor = line.split("-")
        jpn = jpn.strip()
        kor = kor.strip()

        if not name_db.check_full_name_exist(jpn):
            print(f"{jpn} is not in the name database.")
            continue

        name_info = name_db.full_name_db.get(jpn)
        diff = False
        if isinstance(name_info["kor"], str) and kor != name_info["kor"]:
            diff = True
        elif kor not in name_info["kor"]:
            diff = True
        if diff:
            console.print(f"{kor} is different to DB: {name_info['kor']}")


if __name__ == "__main__":
    main()
