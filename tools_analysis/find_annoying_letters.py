import json
from pathlib import Path


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")
    script_base_dir = base_dir / "m2"

    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue
        with open(file, "r") as f:
            src = json.load(f)

        for address, src_dialogue in src.items():
            if "“" in src_dialogue:
                print(file)
                print(address, src_dialogue)


if __name__ == "__main__":
    main()
