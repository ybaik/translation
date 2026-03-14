from pathlib import Path
from module.name_db import NameDB
from module.script import Script


target_files = ["MAIN.EXE", "SNDATA1.CIM", "SNDATA1T.CIM", "SNDATA2.CIM", "SNDATA2T.CIM", "SNDATA3.CIM", "SNDATA3T.CIM"]
# target_files = ["MAIN.EXE"]


def main():
    base_dir = Path("c:/work_han/workspace4")
    script_src_dir = base_dir / "script-pc98-backup"
    bin_base_dir = base_dir / "jpn-pc98"
    out_base_dir = base_dir / "script-pc98"

    for file in script_src_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if "_kor.json" not in file.name:
            continue

        # Check paths
        kor_script_path = file
        jpn_script_path = file.parent / file.name.replace("_kor.json", "_jpn.json")

        kor_out_path = out_base_dir / file.name
        jpn_out_path = out_base_dir / jpn_script_path.name

        if not jpn_script_path.exists():
            print(f"{jpn_script_path.name} is not exists.")
            continue
        bin_name = file.name.replace("_kor.json", "")
        if bin_name not in target_files:
            continue

        # Read source and destination script
        jpn_script = Script(str(jpn_script_path))
        kor_script = Script(str(kor_script_path))

        # Read binary data
        bin_data_path = bin_base_dir / bin_name
        if not Path(bin_data_path).exists():
            print(f"{bin_data_path} does not exist.")
            continue

        with open(bin_data_path, "rb") as f:
            bin_data = f.read()
        bin_data = bytearray(bin_data)

        mod_list_jpn = []
        mod_list_kor = []

        family = True
        keep_family = ""
        has_space = False
        cnt = 0
        for address, sentence in kor_script.script.items():
            start, end = address.split("=")
            start = int(start, 16)
            end = int(end, 16)

            if bin_name == "MAIN.EXE":
                if start < 0x3F964:
                    continue
                if start > 0x41984:
                    continue
            if bin_name in ["SNDATA1.CIM", "SNDATA2.CIM", "SNDATA3.CIM"]:
                if start < 0x1192:
                    continue

            if "0x:" in sentence:
                assert 0, f"{address} is not in the correct format."

            if family:
                has_space = True if "|_" in sentence else False
                keep_family = sentence
            else:
                if has_space:
                    family = not family
                    continue

                length = end - start + 1
                if sentence[-1] == "␀":
                    kor_script.script[address] = sentence.replace("␀", "|_|␀")
                elif length < 6:
                    base_pos = end + 1

                    jpn_sentence = jpn_script.script[address] + "|␀"
                    kor_sentence = sentence + "|_"
                    mod_list_jpn.append([address, f"{start:05X}={base_pos:05X}", jpn_sentence])
                    mod_list_kor.append([address, f"{start:05X}={base_pos:05X}", kor_sentence])
                else:
                    print(length, sentence)
            family = not family

        for info in mod_list_jpn:
            address, address_new, jpn = info
            jpn_script.replace_sentence(address, address_new, jpn)
        for info in mod_list_kor:
            address, address_new, code = info
            kor_script.replace_sentence(address, address_new, code)
        # jpn_script.save(jpn_out_path)
        # kor_script.save(kor_out_path)


if __name__ == "__main__":
    main()
