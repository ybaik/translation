import json
from pathlib import Path


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")
    script_base_dir = base_dir / "script-dos"

    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue
        with open(file, "r", encoding="utf-8") as f:
            src = json.load(f)

        for address, src_sentence in src.items():
            if "“" in src_sentence:
                print(file)
                print(address, src_sentence)


if __name__ == "__main__":
    main()
