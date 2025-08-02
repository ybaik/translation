import json
from pathlib import Path
from rich.console import Console


def main():
    console = Console()
    base_dir = Path("c:/work_han/workspace")
    script_base_dir = base_dir

    script_base_dir = Path("c:/work_han/workspace/script-dos")
    # script_base_dir = Path("c:/work_han/backup")

    find_source = True

    sentence = "|_|_ディスクエラー|_|:|_回復できません"
    sentence_kor = "괜찮으"
    sentence_kor = sentence_kor.replace(" ", "_")

    # Read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories

        file_tag = f"{file.parent.name}/{file.name}"

        if find_source:
            if not "_jpn.json" in file.name:
                continue
            with open(file, "r", encoding="utf-8") as f:
                src = json.load(f)
        else:
            dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
            if not dst_path.exists():
                continue
            with open(dst_path, "r", encoding="utf-8") as f:
                dst = json.load(f)
            with open(file, "r", encoding="utf-8") as f:
                src = json.load(f)

        console.print(file.name)

        # check address
        buf_address = ""
        buf_src_sentence = ""
        buf_dst_sentence = ""

        if not find_source:
            for address, dst_sentence in dst.items():
                if sentence_kor not in dst_sentence:
                    # if sentence_kor != dst_sentence:
                    buf_address = address
                    buf_dst_sentence = dst_sentence
                    buf_src_sentence = src[address]
                    continue

                print("=============================")
                print(buf_address)
                print(buf_src_sentence)
                print(buf_dst_sentence)
                console.print(f"{address} {file_tag}", style="green")
                print(src[address])
                print(dst_sentence)
                print("=============================")
        else:
            for address, src_sentence in src.items():
                if sentence not in src_sentence:
                    buf_address = address
                    buf_src_sentence = src_sentence
                    continue

                #     if not address in dst:
                #         print(f"Key error: {address} {file_tag}")
                #     buf_dst_sentence = dst[address]
                #     continue
                # if address in dst:
                #     dst_sentence = dst[address]
                #     if len(src_sentence) != len(dst_sentence):
                #         print(file.name, address)
                #         assert (
                #             0
                #         ), f"Sentence length is not matched. {len(src_sentence)} != {len(dst_sentence)}"
                #         continue

                print("=============================")
                print(buf_address)
                print(buf_src_sentence)
                # print(buf_dst_sentence)
                console.print(f"{address} {file_tag}", style="green")
                print(src_sentence)
                # print(dst_sentence)
                print("=============================")


if __name__ == "__main__":
    main()
