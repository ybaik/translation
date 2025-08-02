import json
from pathlib import Path
from rich.console import Console
from module.font_table import FontTable


def main():
    console = Console()

    platform = "dos"
    platform = "pc98"

    base_dir = Path("c:/work_han/workspace0")
    ref_base_dir = base_dir
    script_base_dir = base_dir / f"script-{platform}"

    ref = "rb"

    # Read an existing dictionary
    dictionary_path = ref_base_dir / f"{ref}_dictionary.json"
    if not dictionary_path.exists():
        return
    with open(dictionary_path, "r", encoding="utf-8") as f:
        dictionary = json.load(f)

    # Read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        console.print(file.name)
        if not "_jpn.json" in file.name:
            continue
        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        if not dst_path.exists():
            continue

        file_tag = f"{file.parent.name}/{file.name}"
        color = "green"
        with open(file, "r", encoding="utf-8") as f:
            src = json.load(f)
        with open(dst_path, "r", encoding="utf-8") as f:
            dst = json.load(f)

        src_font_table = FontTable("./font_table/font_table-jpn-full.json")
        dst_font_table = FontTable("./font_table/font_table-kor-jin.json")

        # Check addresses in the source script
        modified = False
        for address, src_sentence in src.items():
            if not src_sentence in dictionary:
                continue
            if address not in dst:
                continue

            dst_sentence = dst[address]
            # length = src_font_table.check_length_from_address(address)
            len_src_sentence = src_font_table.check_length_from_sentence(src_sentence)
            len_dst_sentence = dst_font_table.check_length_from_sentence(dst_sentence)
            if len_src_sentence != len_dst_sentence:
                console.print(f"{address},{file_tag}", style=color)
                print(len(src_sentence), len(dst_sentence))
                assert (
                    0
                ), f"Sentence length is not matched. {src_sentence} != {dst_sentence}"
                continue

            # print(file.name, address)
            # print(src_sentence)
            # print(dst_sentence)
            translated = dictionary[src_sentence]["translated"]
            if len(translated) == 1:
                len_translated = dst_font_table.check_length_from_sentence(
                    translated[0]
                )
                if len_dst_sentence != len_translated:
                    console.print(f"Length mismatch: {address},{file_tag}", style="red")
                    continue

                if dst[address] != translated[0]:
                    dst[address] = translated[0]
                    modified = True

                    console.print(f"{address},{file_tag}", style=color)
                    print(src_sentence)
                    print(translated[0])
            # else:
            #     print(len(translated))
            #     print(file.name, address)
            #     print(src_sentence)
            #     print(dst_sentence)

        if modified:
            print(dst_path)
            with open(dst_path, "w", encoding="utf-8") as f:
                json.dump(dst, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
