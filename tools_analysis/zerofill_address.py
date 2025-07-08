import json
from pathlib import Path


# Dialog dictionary
def main():
    # base_dir = Path("c:/work_han/workspace/script")
    base_dir = Path("c:/work_han/font")
    script_base_dir = base_dir
    dst_dir = base_dir

    # read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories

        # Check extensions
        need_continue = True
        # candidates = ["_kor.json", "_jpn.json"]
        # for candidate in candidates:
        #     if candidate in file.name:
        #         need_continue = False
        #         break

        # if need_continue:
        #     continue

        print(file)
        with open(file, "r") as f:
            scripts = json.load(f)
        dst_path = dst_dir / file.name
        with open(dst_path, "w", encoding="utf-8") as f:
            json.dump(scripts, f, ensure_ascii=False, indent=4)

        # scripts_new = dict()
        # for address in scripts.keys():
        #     [code_hex_start, code_hex_end] = address.split("=")
        #     spos = int(code_hex_start, 16)
        #     epos = int(code_hex_end, 16)

        #     # Check sentence length
        #     if epos - spos + 1 != len(scripts[address]) * 2:
        #         print(file.name, address)

        #     address_new = f"{spos:05X}={epos:05X}"
        #     scripts_new[address_new] = scripts[address]

        # dst_path = dst_dir / file.name
        # with open(dst_path, "w", encoding="utf-8") as f:
        #     json.dump(scripts_new, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
