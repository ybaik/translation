from module.name_db import NameDB
from module.script import Script


FILE_CONFIG = {
    "DATA17.DAT": {
        "start": 0x01714,
        "end": 0x01945,
        "name_count": 17,
    },
    "DATA50.DAT": {
        "start": 0x01714,
        "end": 0x019F9,
        "name_count": 53,
    },
    "ODAMAIN.EXE": {
        "start": 0x17724,
        "end": 0x17A09,
        "name_count": 53,
    },
}


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


def pair_korean(text: str) -> str:
    return "".join("{" + text[i : i + 2] + "}" for i in range(0, len(text), 2))


def format_korean_name_mixed_space(fn_kor: str, gn_kor: str):
    """기존 공백 배치 방식을 보관한다."""
    space_added = False
    if len(fn_kor) % 2:
        fn_kor += "_"
        space_added = True
    if len(gn_kor) % 2:
        gn_kor = "_" + gn_kor
        space_added = True

    fn_kor_len = len(fn_kor)
    gn_kor_len = len(gn_kor)
    fn_kor = pair_korean(fn_kor)
    gn_kor = pair_korean(gn_kor)

    if not space_added:
        if gn_kor_len < 6:
            gn_kor_len += 1
            gn_kor = "|_" + gn_kor
        elif fn_kor_len < 6:
            fn_kor_len += 1
            fn_kor += "|_"
        else:
            raise ValueError("Name length is too long.")

    return fn_kor, gn_kor, fn_kor_len, gn_kor_len


def format_korean_name_prefer_given_leading_space(fn_kor: str, gn_kor: str, max_length: int = 6):
    """이름 앞 공간을 우선하면서 모든 한글을 2바이트 묶음 문자로 변환한다."""
    full_name = f"{fn_kor} {gn_kor}"

    if len(fn_kor) % 2:
        fn_kor += "_"
    fn_len = len(fn_kor)
    fn_code = pair_korean(fn_kor)

    if len(gn_kor) % 2:
        gn_kor = "_" + gn_kor
        gn_len = len(gn_kor)
        gn_code = pair_korean(gn_kor)
        given_has_leading_space = True
    elif len(gn_kor) + 1 <= max_length:
        gn_len = len(gn_kor) + 1
        gn_code = "|_" + pair_korean(gn_kor)
        given_has_leading_space = True
    else:
        gn_len = len(gn_kor)
        gn_code = pair_korean(gn_kor)
        given_has_leading_space = False

    if not given_has_leading_space:
        if not fn_kor.endswith("_") and fn_len + 1 <= max_length:
            fn_code += "|_"
            fn_len += 1
        elif not fn_kor.endswith("_"):
            raise ValueError(f"Name length is too long: {full_name} ({fn_len}/{gn_len} bytes)")

    if fn_len > max_length or gn_len > max_length:
        raise ValueError(f"Name length is too long: {full_name} ({fn_len}/{gn_len} bytes)")

    return fn_code, gn_code, fn_len, gn_len


def format_korean_name_without_added_space(
    fn_kor: str,
    gn_kor: str,
    family_max_length: int = 6,
    given_max_length: int = 4,
):
    """성과 이름에 공백을 덧붙이지 않고 2글자 묶음 문자로 변환한다."""
    full_name = f"{fn_kor} {gn_kor}"

    fn_pair_length = len(fn_kor) - len(fn_kor) % 2
    fn_code = pair_korean(fn_kor[:fn_pair_length])
    fn_len = fn_pair_length
    if fn_pair_length < len(fn_kor):
        fn_code += fn_kor[-1]
        fn_len += 2

    gn_pair_length = len(gn_kor) - len(gn_kor) % 2
    gn_code = pair_korean(gn_kor[:gn_pair_length])
    gn_len = gn_pair_length
    if gn_pair_length < len(gn_kor):
        gn_code += gn_kor[-1]
        gn_len += 2

    if fn_len > family_max_length or gn_len > given_max_length:
        raise ValueError(f"Name length is too long: {full_name} ({fn_len}/{gn_len} bytes)")

    return fn_code, gn_code, fn_len, gn_len


def clean_japanese_name(name: str) -> str:
    return name.replace("|_", "").replace("|␀", "").replace("␀", "")


def read_name_arrays(script_jpn: Script, file_name: str):
    config = FILE_CONFIG[file_name]
    entries = []

    for address, sentence in script_jpn.script.items():
        if "=" not in address:
            continue
        start = int(address.split("=", 1)[0], 16)
        if config["start"] <= start <= config["end"]:
            entries.append((address, sentence))

    entries.sort(key=lambda item: int(item[0].split("=", 1)[0], 16))

    name_count = config["name_count"]
    expected_count = name_count * 2
    if len(entries) != expected_count:
        raise ValueError(
            f"{file_name}: expected {expected_count} name entries "
            f"({name_count} family + {name_count} given), got {len(entries)}"
        )

    return entries[:name_count], entries[name_count:]


def make_modification(address: str, length: int, sentence: str):
    start = int(address.split("=", 1)[0], 16)
    new_address = f"{start:05X}={start + length - 1:05X}"
    return address, new_address, sentence


def calculate_modifications(script_jpn: Script, file_name: str, name_db: NameDB, game: str):
    family_names, given_names = read_name_arrays(script_jpn, file_name)
    mod_list_jpn = []
    mod_list_kor = []
    unknown_names = []

    for (fn_address, fn_jpn_raw), (gn_address, gn_jpn_raw) in zip(family_names, given_names):
        fn_jpn = clean_japanese_name(fn_jpn_raw)
        gn_jpn = clean_japanese_name(gn_jpn_raw)
        full_name_jpn = f"{fn_jpn} {gn_jpn}"

        name_info = name_db.full_name_db.get(full_name_jpn)
        if name_info is None or game not in name_info.get("game", []):
            unknown_names.append(full_name_jpn)
            continue

        fn_kor, gn_kor = name_info["kor"].split(" ")
        fn_jpn_len = len(fn_jpn) * 2
        gn_jpn_len = len(gn_jpn) * 2
        fn_kor, gn_kor, fn_kor_len, gn_kor_len = format_korean_name_without_added_space(fn_kor, gn_kor)

        fn_length, fn_jpn, fn_kor = align_length(fn_jpn, fn_kor, fn_jpn_len, fn_kor_len)
        gn_length, gn_jpn, gn_kor = align_length(gn_jpn, gn_kor, gn_jpn_len, gn_kor_len)

        mod_list_jpn.append(make_modification(fn_address, fn_length, fn_jpn))
        mod_list_kor.append(make_modification(fn_address, fn_length, fn_kor))
        mod_list_jpn.append(make_modification(gn_address, gn_length, gn_jpn))
        mod_list_kor.append(make_modification(gn_address, gn_length, gn_kor))

    return mod_list_jpn, mod_list_kor, unknown_names


def print_modifications(file_name: str, mod_list_jpn: list, mod_list_kor: list, unknown_names: list):
    name_count = FILE_CONFIG[file_name]["name_count"]
    converted_count = len(mod_list_jpn) // 2
    print(f"\n[{file_name}] {converted_count}/{name_count} names converted, {len(unknown_names)} unknown")

    for index, (jpn_info, kor_info) in enumerate(zip(mod_list_jpn, mod_list_kor)):
        name_part = "family" if index % 2 == 0 else "given "
        address, address_new, jpn = jpn_info
        _, kor_address_new, kor = kor_info
        print(f"{name_part} JPN {address} -> {address_new}: {jpn}")
        print(f"{name_part} KOR {address} -> {kor_address_new}: {kor}")

    for full_name in unknown_names:
        print(f"unknown: {full_name}")


def save_modifications(
    script_jpn: Script,
    script_kor: Script,
    jpn_path: str,
    kor_path: str,
    mod_list_jpn: list,
    mod_list_kor: list,
):
    for address, address_new, sentence in mod_list_jpn:
        script_jpn.replace_sentence(address, address_new, sentence)
    for address, address_new, sentence in mod_list_kor:
        script_kor.replace_sentence(address, address_new, sentence)

    script_jpn.save(jpn_path)
    script_kor.save(kor_path)


def main():
    ws_num = 0
    base_dir = f"c:/work_han/workspace{ws_num}/script-pc98"
    save = False
    name_db = NameDB()
    game = "nb2"

    for file_name in FILE_CONFIG:
        jpn_path = f"{base_dir}/{file_name}_jpn.json"
        kor_path = f"{base_dir}/{file_name}_kor.json"
        script_jpn = Script(jpn_path)
        script_kor = Script(kor_path)

        mod_list_jpn, mod_list_kor, unknown_names = calculate_modifications(script_jpn, file_name, name_db, game)
        print_modifications(file_name, mod_list_jpn, mod_list_kor, unknown_names)

        if save:
            save_modifications(
                script_jpn,
                script_kor,
                jpn_path,
                kor_path,
                mod_list_jpn,
                mod_list_kor,
            )


if __name__ == "__main__":
    main()
