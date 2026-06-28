"""텍스트 파일에서 인명 DB를 추가하거나 갱신한다.

입력 파일은 UTF-8로 저장하며 빈 줄을 넣지 않는다.

main_full() 형식(한 줄에 전체 이름 하나):
    일본성 일본이름 - 한국성 한국이름

예:
    蛎崎 慶広 - 카키자키 요시히로
    葦名 盛氏 - 아시나 모리우지

일본어와 한국어 양쪽 모두 성과 이름 사이에 공백이 정확히 하나 필요하다.
좌우 전체 이름은 하이픈(-) 하나로 구분한다. 한국어 이름에 물음표(?)가
포함된 줄은 처리하지 않는다.

main_half() 형식(성 한 줄과 이름 한 줄을 한 쌍으로 입력):
    일본성:한국성
    일본이름:한국이름

예:
    蛎崎:카키자키
    慶広:요시히로

파일 아래의 __main__ 블록에서 사용할 함수를 선택하고, 선택한 함수 안에서
game, ws_num과 입력 파일 경로를 설정한다.
DB 파일에 실제로 반영하려면 해당 함수 끝의 name_db.save_db() 주석을 해제한다.
"""

from module.name_db import NameDB


def main_half():
    name_db = NameDB()
    game = "nb2"

    base_dir = "c:/work_han/workspace0/ss.txt"
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
    game = "nb2"
    ws_num = 0
    base_dir = f"c:/work_han/workspace{ws_num}/ss.txt"
    with open(base_dir, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        jpn, kor = line.split("-")
        full_name_jpn = jpn.strip()
        full_name_kor = kor.strip()

        if "?" in full_name_kor:
            continue

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
