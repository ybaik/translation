from pathlib import Path
from module.script import Script
from module.name_db import NameDB


def split_and_pair(text: str, pairs: list) -> bool:
    space_included = False
    for i in range(0, len(text), 2):
        pair = text[i : i + 2]

        # 길이가 1이면 뒤에 "_" 추가
        if len(pair) == 1:
            pair += "_"
            space_included = True

        assert " " not in pair, f"Input text include space: {text}"

        pairs.append(pair)
    return space_included


def main():
    # To add 1byte space to the family name for isolating the given name
    # Only apply to the limited address range
    ws_num = 4
    game = f"nb{ws_num}"

    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    script_base_dir = base_dir / "script-pc98"
    bin_base_dir = base_dir / "jpn-pc98"
    name_db = NameDB()
    db = dict()
    db_gn = dict()
    for k, v in name_db.full_name_db.items():
        if game not in v["game"]:
            continue
        # family name
        db[k.split(" ")[0]] = v["kor"].split(" ")[0]
        # given name
        db_gn[k.split(" ")[-1]] = v["kor"].split(" ")[-1]

    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        print(file.name)
        if "_kor.json" not in file.name:
            continue

        # Check paths
        kor_script_path = file
        jpn_script_path = file.parent / file.name.replace("_kor.json", "_jpn.json")
        if not jpn_script_path.exists():
            print(f"{jpn_script_path.name} is not exists.")
            continue

        # Read source and destination script
        jpn_script = Script(str(jpn_script_path))
        kor_script = Script(str(kor_script_path))

        # Read the source binary data
        bin_data_path = bin_base_dir / str(file.relative_to(script_base_dir)).replace("_kor.json", "")

        if not Path(bin_data_path).exists():
            print(f"{bin_data_path} does not exist.")
            continue

        with open(bin_data_path, "rb") as f:
            bin_data = f.read()
        bin_data = bytearray(bin_data)

        mod_list_jpn = []
        mod_list_kor = []

        for address, jpn_sentence in jpn_script.script.items():
            start, end = address.split("=")
            start = int(start, 16)
            end = int(end, 16)

            # if address == "400FF=40102":
            #     print(address)

            # Check address limit for the specific file

            if game == "nb3":
                if "MAIN.EXE" in file.name:
                    if start < 0x24C6A or start > 0x26FED:
                        continue
                if "SNDATA1.CIM" in file.name:
                    if start < 0xD38:
                        continue
                if "SNDATA2.CIM" in file.name:
                    if start < 0xD38:
                        continue
            elif game == "nb4":
                if "MAIN.EXE" in file.name:
                    if start < 0x3F964 or start > 0x41984:
                        continue
                if "SNDATA1.CIM" in file.name:
                    if start < 0x1192:
                        continue
                if "SNDATA2.CIM" in file.name:
                    if start < 0x1192:
                        continue
                if "SNDATA3.CIM" in file.name:
                    if start < 0x1192:
                        continue
            else:
                continue

            kor_sentence = kor_script.script[address]

            # Check 1-byte null count
            jpn_byte_add = jpn_sentence.count("|␀")
            jpn_sentence_filtered = jpn_sentence.replace("|␀", "")
            jpn_byte_add += jpn_sentence_filtered.count("␀") * 2
            jpn_sentence_filtered = jpn_sentence_filtered.replace("␀", "")

            # Find new name from DB
            if jpn_sentence_filtered not in db:
                continue

            # Check if the name is in the given name database
            if jpn_sentence_filtered in db_gn:
                print(f"{jpn_sentence_filtered}:{kor_sentence} - in given name database")
                continue

            jpn_byte_filtered = len(jpn_sentence_filtered) * 2

            content = db[jpn_sentence_filtered]
            kor_sentence_new = ""
            pairs = []
            space_included = split_and_pair(content, pairs)
            for pair in pairs:
                kor_sentence_new += f"{{{pair}}}"
            kor_byte = len(pairs) * 2

            if not space_included:
                kor_sentence_new += "|_"
                kor_byte += 1

            diff = jpn_byte_filtered - kor_byte

            if diff == 0 and jpn_byte_add:
                base_pos = end - jpn_byte_add
                mod_list_jpn.append([address, f"{start:05X}={base_pos:05X}", jpn_sentence_filtered])
                mod_list_kor.append([address, f"{start:05X}={base_pos:05X}", kor_sentence_new])
            elif diff >= 0:
                if diff // 2:
                    kor_sentence_new += "␀" * (diff // 2)
                if diff % 2:
                    kor_sentence_new += "|␀"
                kor_script.script[address] = kor_sentence_new

            elif diff < 0:
                # Need to check binary in jpn
                base_pos = end - jpn_byte_add
                search_space = bin_data[base_pos + 1 : base_pos - diff + 1]
                is_all_zero = all(b == 0 for b in search_space)

                if is_all_zero:
                    jpn_sentence_new = jpn_sentence_filtered
                    if (-diff) // 2:
                        jpn_sentence_new += "␀" * (-diff // 2)
                    if (-diff) % 2:
                        jpn_sentence_new += "|␀"
                    mod_list_jpn.append([address, f"{start:05X}={base_pos - diff:05X}", jpn_sentence_new])
                    mod_list_kor.append([address, f"{start:05X}={base_pos - diff:05X}", kor_sentence_new])
                else:
                    print(f"Address mismatch: {address},{jpn_sentence},{kor_sentence}")

        for info in mod_list_jpn:
            address, address_new, jpn = info
            jpn_script.replace_sentence(address, address_new, jpn)
        for info in mod_list_kor:
            address, address_new, code = info
            kor_script.replace_sentence(address, address_new, code)

        jpn_script.save(jpn_script_path)
        kor_script.save(kor_script_path)


if __name__ == "__main__":
    main()
