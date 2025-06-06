import json
from pathlib import Path


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace4")
    script_base_dir = base_dir
    data_base_dir = base_dir / "m4_kor"

    find_source = True

    sentence = "VT-102!"
    sentence_kor = "기록참모 엑세돌 "
    sentence_kor = sentence_kor.replace(" ", "_")

    # read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue
        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        if not dst_path.exists():
            continue

        with open(file, "r", encoding="utf-8") as f:
            src = json.load(f)
        with open(dst_path, "r", encoding="utf-8") as f:
            dst = json.load(f)

        # check address
        buf_address = ""
        buf_src_sentence = ""
        buf_dst_sentence = ""

        if not find_source:
            for address, dst_sentence in dst.items():
                if sentence_kor not in dst_sentence:
                    buf_address = address
                    buf_dst_sentence = dst_sentence
                    buf_src_sentence = src[address]
                    continue

                print("=============================")
                print(buf_address)
                print(buf_src_sentence)
                print(buf_dst_sentence)
                print(file.name, address)
                print(src[address])
                print(dst_sentence)
                print("=============================")
        else:
            for address, src_sentence in src.items():
                if sentence not in src_sentence:
                    buf_address = address
                    buf_src_sentence = src_sentence
                    buf_dst_sentence = dst[address]
                    continue
                if address in dst:
                    dst_sentence = dst[address]
                    if len(src_sentence) != len(dst_sentence):
                        print(file.name, address)
                        assert (
                            0
                        ), f"Sentence length is not matched. {len(src_sentence)} != {len(dst_sentence)}"
                        continue

                    print("=============================")
                    print(buf_address)
                    print(buf_src_sentence)
                    print(buf_dst_sentence)
                    print(file.name, address)
                    print(src_sentence)
                    print(dst_sentence)
                    print("=============================")


if __name__ == "__main__":
    main()
