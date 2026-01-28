import json
from pathlib import Path
from rich.console import Console
from module.font_table import FontTable


def main():
    console = Console()

    ws_num = 4
    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    script_dirs = [
        base_dir / "script-dos",
        base_dir / "script-pc98",
    ]

    # ,"s":0
    # ,"s":1

    # Read an existing dictionary
    annoying_path = base_dir / "annoying.json"
    # annoying_path = base_dir / f"{ref}_dictionary.json"
    if not annoying_path:
        return
    with open(annoying_path, "r", encoding="utf-8") as f:
        annoying = json.load(f)

    print(f"Number of annoying scripts = {len(annoying)}")

    # Read a pair of scripts
    for script_dir in script_dirs:
        src_font_table = FontTable(Path("./font_table/font_table-jpn-full.json"), script_dir)
        dst_font_table = FontTable(Path("./font_table/font_table-kor-jin.json"), script_dir)

        custom_word_path = script_dir / "custom_word.json"
        custom_words = {}
        if custom_word_path.exists():
            with open(custom_word_path, "r", encoding="utf-8") as f:
                custom_words = json.load(f)

        for file in script_dir.rglob("*.json"):  # Use rglob to search subdirectories
            if "_jpn.json" not in file.name:
                continue

            console.print(file.name)
            file_tag = f"{file.parent.name}/{file.name}"
            color = "green"
            dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
            if not dst_path.exists():
                continue

            with open(file, "r", encoding="utf-8") as f:
                src = json.load(f)
            with open(dst_path, "r", encoding="utf-8") as f:
                dst = json.load(f)

            # Check addresses in the source script
            modified = False
            for address, src_sentence in src.items():
                if "=" not in address:
                    continue
                if src_sentence not in annoying:
                    continue

                if address not in dst:
                    continue

                length_from_src_sentence = src_font_table.check_length_from_sentence(
                    sentence=src_sentence, custom_words=custom_words
                )
                # length_from_src_sentence = src_font_table.verify_sentence(src_sentence)
                dst_sentence = dst[address]
                length_from_dst_sentence = dst_font_table.check_length_from_sentence(
                    sentence=dst_sentence, custom_words=custom_words
                )
                # length_from_dst_sentence = dst_font_table.verify_sentence(dst_sentence)

                if length_from_src_sentence != length_from_dst_sentence:
                    console.print(f"{address},{file_tag}", style=color)
                    assert 0, f"Sentence length is not matched. {src_sentence} != {dst_sentence}"
                    continue

                # print(file.name, address)
                # print(src_sentence)
                # print(dst_sentence)
                # print(1)
                # if annoying[src_sentence]["count"] > 1:
                #     continue
                # new_sentence = annoying[src_sentence]["translated"][0]
                # if new_sentence != dst_sentence:
                #     dst[address] = new_sentence
                #     modified = True

                if "s" in annoying[src_sentence]:
                    idx = annoying[src_sentence]["s"]
                    new_sentence = annoying[src_sentence]["translated"][idx]
                    if new_sentence != dst_sentence:
                        dst[address] = new_sentence
                        console.print(f"{address},{file_tag}", style=color)
                        print(new_sentence)
                        modified = True

            if modified:
                with open(dst_path, "w", encoding="utf-8") as f:
                    json.dump(dst, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
