from pathlib import Path
from module.name_db import NameDB
from module.script import Script

base_dir = Path("c:/work_han/workspace4")
script_dir = base_dir / "script-pc98"

name_db = NameDB()

for file in script_dir.rglob("*.json"):  # Use rglob to search subdirectories
    if "_kor.json" not in file.name:
        continue

    if "SNDATA3T.CIM" not in file.name:
        continue

    # Check paths
    kor_script_path = file

    kor_script = Script(str(kor_script_path))

    family = True

    for address, sentence in kor_script.script.items():
        start, end = address.split("=")
        start = int(start, 16)
        end = int(end, 16)

        if "MAIN.EXE" in file.name:
            if start < 0x40E88:
                continue
            if start > 0x41984:
                continue
        if "SNDATA2.CIM" in file.name or "SNDATA3.CIM" in file.name:
            if start < 0x1192:
                continue

        if "␀" in sentence:
            family = not family
            continue

        if "0x:" in sentence and "#" not in sentence:
            family = not family
            continue
        if "{" in sentence:
            family = not family
            continue

        # check sentence length - byte
        length = 0
        if "0x:" in sentence:
            code, name = sentence[3:].split("#")
            name = name.strip()
            length = len(code) // 2
        else:
            name = sentence
            length = len(name) * 2

        new_sentence = ""

        def split_and_pair(text: str):
            space = False
            output = ""
            for i in range(0, len(text), 2):
                pair = text[i : i + 2]

                # 길이가 1이면 뒤에 "_" 추가
                if len(pair) == 1:
                    space = True
                    output += f"{{{pair}|_}}"
                else:
                    output += f"{{{pair}}}"
            return space, i, output

        space, cnt, new_sentence = split_and_pair(name)

        if length > cnt * 2:
            if (not space) and family:
                new_sentence += "|_|␀"
            else:
                new_sentence += "␀"

        print(new_sentence, space, family)
        family = not family

        kor_script.script[address] = new_sentence
    kor_script.save(kor_script_path)
