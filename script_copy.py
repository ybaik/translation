import os
import json
import shutil
from pathlib import Path


def main():
    base_dir = Path("c:/work_han/workspace")

    script_base_dir = base_dir / "script"
    dst_dir = base_dir / "script"

    count = 0
    for file in script_base_dir.rglob("*.json"):
        if not "_jpn.json" in file.name:
            continue

        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        # copy file with the new name
        shutil.copy(file, dst_path)

        # dst_path = dst_dir / file.name
        # shutil.copy(file, dst_path)

        # src_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        # dst_path = dst_dir / file.name.replace("_jpn.json", "_kor.json")
        # shutil.copy(src_path, dst_path)

        print(file)
        # bin_path = bin_base_dir / file.name.replace("_jpn.json", "")
        # dst_path = bin_copy_dir / file.name.replace("_jpn.json", "")
        # shutil.copy(bin_path, dst_path)

        # format 변경
        # with open(file, "r") as f:
        #     src = json.load(f)

        # dst = dict()
        # for address, src_dialogue in src.items():
        #     address_new = address.replace("0x", "").upper()
        #     dst[address_new] = src_dialogue

        # with open(file, "w") as f:
        #     json.dump(dst, f, ensure_ascii=False, indent=4)
    print(count)


if __name__ == "__main__":
    main()
