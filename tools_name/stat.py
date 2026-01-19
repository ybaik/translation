from module.name_db import NameDB


def main():
    name_db = NameDB()
    query = {"game": ["nobu4"]}
    print(f"{name_db.check_number(query)} - 노부나가의 야망 4")
    query = {"game": ["taiko2"]}
    print(f"{name_db.check_number(query)} - 태합입지전 2")
    query = {"game": ["nobu4", "taiko2"]}
    print(f"{name_db.check_number(query)} - 태합입지전 2 & 노부나가의 야망 4")
    print(f"{name_db.check_number()} - Total")
    name_db.print_duplicate()


if __name__ == "__main__":
    main()
