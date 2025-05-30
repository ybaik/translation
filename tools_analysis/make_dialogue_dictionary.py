import json
from pathlib import Path


def main():
    base_dir = Path("c:/work_han/workspace")

    ref = "m3"
    src = "m2"
    script_base_dir = base_dir / src

    reference_dictionary_path = base_dir / ref / f"{ref}_dictionary.json"
    with open(reference_dictionary_path, "r") as f:
        dictionary = json.load(f)
    # dictionary = dict()

    # read a dictionary
    dictionary_path = base_dir / f"{src}_dictionary.json"
    annoying_path = base_dir / f"{src}_annoying.json"

    # read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue
        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        if not dst_path.exists():
            continue

        with open(file, "r") as f:
            src = json.load(f)
        with open(dst_path, "r") as f:
            dst = json.load(f)

        # check address
        for address, src_dialogue in src.items():
            if not src_dialogue in dictionary:
                dictionary[src_dialogue] = {
                    "count": 0,
                    "reference": 0,
                    "translated": [],
                }

            if address in dst:
                dst_dialogue = dst[address]
                if len(src_dialogue) != len(dst_dialogue):
                    print(file.name, address)
                    assert (
                        0
                    ), f"Dialogue length is not matched. {address}/{len(src_dialogue)} != {len(dst_dialogue)}"
                    continue
                dictionary[src_dialogue]["reference"] += 1
                if not dst_dialogue in dictionary[src_dialogue]["translated"]:
                    dictionary[src_dialogue]["count"] += 1
                    dictionary[src_dialogue]["translated"].append(dst_dialogue)

    # save dictionary
    with open(dictionary_path, "w") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)

    # make annoying dictionary
    annoying = dict()
    for key, value in dictionary.items():
        if value["count"] > 1:
            annoying[key] = value

    print("Number of scripts = ", len(dictionary))
    print("Number of annoying scripts = ", len(annoying))

    # save dictionary
    with open(annoying_path, "w") as f:
        json.dump(annoying, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
