from module.name_db import NameDB
from module.script import Script
from rich.console import Console


def align_length(jpn: str, kor: str, jpn_len: int, kor_len: int):
    length = jpn_len
    diff = kor_len - jpn_len
    if diff > 0:  # Kor이 더 크다
        if diff // 2:
            jpn += "␀" * (diff // 2)
        if diff % 2:
            jpn += "|␀"
        length = kor_len
    elif diff < 0:  # Jpn이 더 크다
        diff *= -1
        if diff // 2:
            kor += "␀" * (diff // 2)
        if diff % 2:
            kor += "|␀"
    return length, jpn, kor


def main():
    console = Console()
    name_db = NameDB()
    game = "taiko1"
    ws_num = 1
    base_dir = f"c:/work_han/workspace{ws_num}/script-pc98"

    for file_name in ["TBS.DAT", "MAIN.EXE"]:
        script_jpn = Script(f"{base_dir}/{file_name}_jpn.json")
        script_kor = Script(f"{base_dir}/{file_name}_kor.json")

        fn_jpn_raw = ""
        gn_jpn_raw = ""
        fn_address = ""
        mod_list_jpn = []
        mod_list_kor = []

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

            if len(fn_jpn_raw) == 0:
                fn_jpn_raw = sentence
                fn_address = address
                continue

            if len(gn_jpn_raw) == 0:
                gn_jpn_raw = sentence

            fn_jpn = fn_jpn_raw.replace("␀", "").replace("|␀", "").replace("|_", "")
            gn_jpn = gn_jpn_raw.replace("␀", "").replace("|␀", "").replace("|_", "")

            full_name_jpn_clean = f"{fn_jpn} {gn_jpn}"

            if not name_db.check_full_name_exist(full_name_jpn_clean):
                print(f"{full_name_jpn_clean} is not in the name DB")
                fn_jpn_raw = ""
                gn_jpn_raw = ""
                continue

            fn_kor, gn_kor = name_db.full_name_db[full_name_jpn_clean]["kor"].split(" ")

            space_added = False
            if len(fn_kor) % 2:
                fn_kor += "_"
                space_added = True
            if len(gn_kor) % 2:
                gn_kor = "_" + gn_kor
                space_added = True

            fn_jpn_len = len(fn_jpn) * 2
            fn_kor_len = len(fn_kor)
            gn_jpn_len = len(gn_jpn) * 2
            gn_kor_len = len(gn_kor)

            fn_kor = "".join("{" + fn_kor[i : i + 2] + "}" for i in range(0, len(fn_kor), 2))
            gn_kor = "".join("{" + gn_kor[i : i + 2] + "}" for i in range(0, len(gn_kor), 2))

            if not space_added:
                if gn_kor_len < 6:
                    gn_kor_len += 1
                    gn_kor = "|_" + gn_kor
                elif fn_kor_len < 6:
                    fn_kor_len += 1
                    fn_kor += "|_"
                else:
                    assert 0, f"Name length is too long: {full_name_jpn_clean}"

            # Compare length of jpn and kor
            fn_length, fn_jpn, fn_kor = align_length(fn_jpn, fn_kor, fn_jpn_len, fn_kor_len)
            gn_length, gn_jpn, gn_kor = align_length(gn_jpn, gn_kor, gn_jpn_len, gn_kor_len)

            # Set FN
            start, end = fn_address.split("=")
            start = int(start, 16)
            mod_list_jpn.append([fn_address, f"{start:05X}={start + fn_length - 1:05X}", fn_jpn])
            mod_list_kor.append([fn_address, f"{start:05X}={start + fn_length - 1:05X}", fn_kor])

            # Set GN
            start, end = address.split("=")
            start = int(start, 16)
            mod_list_jpn.append([address, f"{start:05X}={start + gn_length - 1:05X}", gn_jpn])
            mod_list_kor.append([address, f"{start:05X}={start + gn_length - 1:05X}", gn_kor])

            fn_jpn_raw = ""
            gn_jpn_raw = ""

        for info in mod_list_jpn:
            address, address_new, jpn = info
            script_jpn.replace_sentence(address, address_new, jpn)
        for info in mod_list_kor:
            address, address_new, code = info
            script_kor.replace_sentence(address, address_new, code)

        script_jpn.save(f"{base_dir}/{file_name}_jpn.json")
        script_kor.save(f"{base_dir}/{file_name}_kor.json")


if __name__ == "__main__":
    main()
