import json
from pathlib import Path


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")
    script_base_dir = base_dir

    # read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_dos.json" in file.name:
            continue

        print(file)

        with open(file, "r") as f:
            scripts = json.load(f)

        scripts_new = dict()
        for address in scripts.keys():
            [code_hex_start, code_hex_end] = address.split("=")
            spos = int(code_hex_start, 16)
            epos = int(code_hex_end, 16)

            # Check sentence length
            if epos - spos + 1 != len(scripts[address]) * 2:
                print(file.name, address)

            address_new = f"{spos:05X}={epos:05X}"
            scripts_new[address_new] = scripts[address]

        with open(file, "w") as f:
            json.dump(scripts_new, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
