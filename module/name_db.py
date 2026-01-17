import json
from pathlib import Path


def read_name_db(name_db_path: Path) -> dict:
    if name_db_path.exists():
        with open(name_db_path, "r", encoding="utf-8") as f:
            name_db = json.load(f)
    else:
        name_db = dict()
    return name_db


class NameDB:
    def __init__(self) -> None:
        self.full_name_db = dict()
        self.family_name_db = dict()
        self.given_name_db = dict()
        self.read_db()

    def read_db(self) -> None:
        self.full_name_db = read_name_db(Path("name_db/full_name_db.json"))
        self.family_name_db = read_name_db(Path("name_db/family_name_db.json"))
        self.given_name_db = read_name_db(Path("name_db/given_name_db.json"))

    def save_db(self) -> None:
        self.full_name_db = {k: v for k, v in sorted(self.full_name_db.items())}
        self.family_name_db = {k: v for k, v in sorted(self.family_name_db.items())}
        self.given_name_db = {k: v for k, v in sorted(self.given_name_db.items())}

        # Save the name db
        with open("name_db/full_name_db.json", "w", encoding="utf-8") as f:
            json.dump(self.full_name_db, f, ensure_ascii=False, indent=4)
        with open("name_db/family_name_db.json", "w", encoding="utf-8") as f:
            json.dump(self.family_name_db, f, ensure_ascii=False, indent=4)
        with open("name_db/given_name_db.json", "w", encoding="utf-8") as f:
            json.dump(self.given_name_db, f, ensure_ascii=False, indent=4)

    def check_full_name_exist(self, full_name: str) -> bool:
        if full_name in self.full_name_db.keys():
            return True
        return False

    def check_family_name_exist(self, family_name: str) -> bool:
        if family_name in self.family_name_db.keys():
            return True
        return False

    def check_given_name_exist(self, given_name: str) -> bool:
        if given_name in self.family_name_db.keys():
            return True
        return False

    def check_number(self, query: dict = dict()) -> int:
        count = 0
        for k, v in self.full_name_db.items():
            if query.get("game") is not None:
                game = query["game"]
                if game not in v["game"]:
                    continue

            count += 1
        return count

    def print_duplicate(self) -> None:
        for k, v in self.family_name_db.items():
            if len(v) > 1:
                print(f"성: {k}", v)
        for k, v in self.given_name_db.items():
            if len(v) > 1:
                print(f"이름: {k}", v)

    def add_full_name(self, full_name: str, kor: str, game: str) -> None:
        if full_name in self.full_name_db.keys():
            # Check difference
            if kor != self.full_name_db[full_name]["kor"]:
                assert 0, f"{full_name} {self.full_name_db[full_name]['kor']} is different to {kor}."
            # check game
            if game not in self.full_name_db[full_name]["game"]:
                self.full_name_db[full_name]["game"].append(game)
        else:
            self.full_name_db[full_name] = {"kor": kor, "game": [game]}

        family_name_jpn, given_name_jpn = full_name.split(" ")
        family_name_kor, given_name_kor = kor.split(" ")

        # add family name
        if family_name_jpn in self.family_name_db.keys():
            if family_name_kor not in self.family_name_db[family_name_jpn]:
                assert 0, (
                    f"Family name: {family_name_jpn} {family_name_kor} is different to {self.family_name_db[family_name_jpn]}."
                )
        else:
            self.family_name_db[family_name_jpn] = [family_name_kor]

        # add given name
        if given_name_jpn in self.given_name_db.keys():
            if given_name_kor not in self.given_name_db[given_name_jpn]:
                assert 0, (
                    f"Given name: {given_name_jpn} {given_name_kor} is different to {self.given_name_db[given_name_jpn]}."
                )
        else:
            self.given_name_db[given_name_jpn] = [given_name_kor]
