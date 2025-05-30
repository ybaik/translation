import json
from pathlib import Path


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")

    ref = "m3"
    src = "m3"
    script_base_dir = base_dir / src

    # read a dictionary
    annoying_path = base_dir / f"{ref}_annoying.json"
    # annoying_path = base_dir / f"{ref}_dictionary.json"
    if not annoying_path:
        return
    with open(annoying_path, "r") as f:
        annoying = json.load(f)

    print(f"Number of annoying scripts = {len(annoying)}")

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
        modified = False
        for address, src_dialogue in src.items():
            if not src_dialogue in annoying:
                continue

            if address in dst:
                dst_dialogue = dst[address]
                if len(src_dialogue) != len(dst_dialogue):
                    print(file.name, address)
                    assert (
                        0
                    ), f"Dialogue length is not matched. {src_dialogue} != {dst_dialogue}"
                    continue

                # print(file.name, address)
                # print(src_dialogue)
                # print(dst_dialogue)
                # print(1)
                # if annoying[src_dialogue]["count"] > 1:
                #     continue
                # new_dialogue = annoying[src_dialogue]["translated"][0]
                # if new_dialogue != dst_dialogue:
                #     dst[address] = new_dialogue
                #     modified = True

                if "modify" in annoying[src_dialogue]:
                    idx = annoying[src_dialogue]["modify"]
                    new_dialogue = annoying[src_dialogue]["translated"][idx]
                    if new_dialogue != dst_dialogue:
                        dst[address] = new_dialogue
                        print(file.name, address)
                        print(new_dialogue)
                        modified = True

        if modified:
            with open(dst_path, "w") as f:
                json.dump(dst, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
