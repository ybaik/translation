from module.name_db import NameDB


def main():
    name_db = NameDB()
    game = "노부나가의 야망 4"

    query = {"game": [game]}
    print(f"{name_db.check_number(query)} - 노부나가의 야망 4")
    query = {"game": ["태합입지전 2"]}
    print(f"{name_db.check_number(query)} - 태합입지전 2")
    query = {"game": [game, "태합입지전 2"]}
    print(f"{name_db.check_number(query)} - 태합입지전 2 & 노부나가의 야망 4")
    print(f"{name_db.check_number()} - Total")
    name_db.print_duplicate()


if __name__ == "__main__":
    main()
