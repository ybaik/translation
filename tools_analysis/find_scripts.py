import json
from pathlib import Path


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")
    script_base_dir = base_dir / "m2"
    script_base_dir = base_dir
    data_base_dir = base_dir / "m2_kor"

    find_source = True

    dialogue = "|"
    dialogue_kor = "기록참모 엑세돌 "
    dialogue_kor = dialogue_kor.replace(" ", "_")

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
        buf_address = ""
        buf_src_dialogue = ""
        buf_dst_dialogue = ""

        if not find_source:
            for address, dst_dialogue in dst.items():
                if dialogue_kor not in dst_dialogue:
                    buf_address = address
                    buf_dst_dialogue = dst_dialogue
                    buf_src_dialogue = src[address]
                    continue

                print("=============================")
                print(buf_address)
                print(buf_src_dialogue)
                print(buf_dst_dialogue)
                print(file.name, address)
                print(src[address])
                print(dst_dialogue)
                print("=============================")
        else:
            for address, src_dialogue in src.items():
                if dialogue != src_dialogue:
                    buf_address = address
                    buf_src_dialogue = src_dialogue
                    buf_dst_dialogue = dst[address]
                    continue
                if address in dst:
                    dst_dialogue = dst[address]
                    if len(src_dialogue) != len(dst_dialogue):
                        print(file.name, address)
                        assert (
                            0
                        ), f"Dialogue length is not matched. {src_dialogue} != {dst_dialogue}"
                        continue

                    print("=============================")
                    print(buf_address)
                    print(buf_src_dialogue)
                    print(buf_dst_dialogue)
                    print(file.name, address)
                    print(src_dialogue)
                    print(dst_dialogue)
                    print("=============================")


if __name__ == "__main__":
    main()
