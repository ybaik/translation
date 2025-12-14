import json
from pathlib import Path
from rich.console import Console
from module.script import Script


def main():
    console = Console()
    base_dir = Path("c:/work_han/workspace2")
    script_base_dir = base_dir

    script_base_dir = Path("c:/work_han/workspace2/script-pc98")
    # script_base_dir = Path("c:/work_han/backup")

    find_source = False
    restriction = False
    print_correspond_sentence = False

    sentence = ""
    sentence_kor = "정말이지,"
    sentence_kor = sentence_kor.replace(" ", "_")

    # Read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        file_tag = f"{file.parent.name}/{file.name}"

        if "_jpn.json" not in file.name:
            continue

        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        if not dst_path.exists():
            continue

        src_script = Script(str(file))
        dst_script = Script(str(dst_path))
        # console.print(file.name)

        # check address
        buf_address = ""
        buf_src_sentence = ""
        buf_dst_sentence = ""

        if not find_source:
            for address, dst_sentence in dst_script.script.items():
                found = False
                if restriction:
                    if sentence_kor == dst_sentence:
                        found = True
                else:
                    if sentence_kor in dst_sentence:
                        found = True
                if not found:
                    # if sentence_kor != dst_sentence:
                    buf_address = address
                    buf_dst_sentence = dst_sentence
                    buf_src_sentence = src_script.script[address]
                    continue

                print("=============================")
                # print(buf_address)
                # print(buf_src_sentence)
                # print(buf_dst_sentence)
                console.print(f"{address} {file_tag}", style="green")
                print(src_script.script[address])
                print(dst_sentence)
                print("=============================")
        else:
            for address, src_sentence in src_script.script.items():
                found = False
                if restriction:
                    if sentence == src_sentence:
                        found = True
                else:
                    if sentence in src_sentence:
                        found = True
                if not found:
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
                # print(buf_address)
                # print(buf_src_sentence)
                # print(buf_dst_sentence)
                console.print(f"{address} {file_tag}", style="green")
                print(src_sentence)
                print(dst_script.script[address])
                print("=============================")


if __name__ == "__main__":
    main()
