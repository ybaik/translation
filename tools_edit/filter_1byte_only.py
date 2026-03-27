import json
from pathlib import Path
from rich.console import Console
from module.script import Script


def main():
    ws_num = 2
    platform = "pc98"
    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    script_dir = base_dir / f"script-{platform}"

    for file in script_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if "_jpn.json" not in file.name:
            continue

        if "BSDATA" not in file.name:
            continue

        script = Script(str(file))

        list_to_delete = []
        for address, sentence in script.script.items():
            if "0x:" in sentence:
                continue
            length = len(sentence)
            cnt_1byte = sentence.count("|")
            if length // 2 == cnt_1byte:
                list_to_delete.append(address)

        if len(list_to_delete):
            for address in list_to_delete:
                script.script.pop(address)
            script.save(file)


if __name__ == "__main__":
    main()
