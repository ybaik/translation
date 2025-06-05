import json
from pathlib import Path


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")

    script_base_dir = base_dir

    ref = "m2"
    # read a dictionary
    dictionary_path = base_dir / f"{ref}_dictionary.json"
    if not dictionary_path.exists():
        return
    with open(dictionary_path, "r") as f:
        dictionary = json.load(f)

    # read a pair of scripts
    for file in script_base_dir.glob("*.json"):  # Use rglob to search subdirectories
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
        for address, src_sentence in src.items():
            if not src_sentence in dictionary:
                continue

            if address in dst:
                dst_sentence = dst[address]
                if len(src_sentence) != len(dst_sentence):
                    print(file.name, address)
                    assert (
                        0
                    ), f"Sentence length is not matched. {src_sentence} != {dst_sentence}"
                    continue

                # print(file.name, address)
                # print(src_sentence)
                # print(dst_sentence)
                translated = dictionary[src_sentence]["translated"]

                if len(translated) == 1:
                    if dst[address] != translated[0]:
                        dst[address] = translated[0]
                        modified = True
                        print(file.name, address)
                        print(src_sentence)
                        print(translated[0])
                # else:
                #     print(len(translated))
                #     print(file.name, address)
                #     print(src_sentence)
                #     print(dst_sentence)

        if modified:
            print(dst_path)
            with open(dst_path, "w") as f:
                json.dump(dst, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
