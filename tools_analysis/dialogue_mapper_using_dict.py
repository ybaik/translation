import json
from pathlib import Path
from rich.console import Console
from module.script import Script
from module.font_table import FontTable


def main():
    console = Console()

    platform = "dos"
    platform = "pc98"
    ws_num = 3
    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    ref_base_dir = base_dir
    script_base_dir = base_dir / f"script-{platform}"

    # Read an existing dictionary
    dictionary_path = ref_base_dir / "dictionary.json"
    if not dictionary_path.exists():
        return
    with open(dictionary_path, "r", encoding="utf-8") as f:
        dictionary = json.load(f)

    # Read a custom word dictionary
    custom_word_path = script_base_dir / "custom_word.json"
    custom_words = {}
    if custom_word_path.exists():
        with open(custom_word_path, "r", encoding="utf-8") as f:
            custom_words = json.load(f)

    # Read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        console.print(file.name)

        if "_jpn.json" not in file.name:
            continue
        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        if not dst_path.exists():
            continue

        file_tag = f"{file.parent.name}/{file.name}"
        color = "green"

        src_script = Script(str(file))
        dst_script = Script(str(dst_path))

        src_font_table = FontTable(
            file_path=Path("./font_table/font_table-jpn-full.json"), custom_char_dir=script_base_dir
        )
        dst_font_table = FontTable(
            file_path=Path("./font_table/font_table-kor-jin.json"), custom_char_dir=script_base_dir
        )

        # Check addresses in the source script
        modified = False
        for address, src_sentence in src_script.script.items():
            if "=" not in address:
                continue

            if src_sentence not in dictionary:
                continue
            if address not in dst_script.script:
                continue

            dst_sentence = dst_script.script[address]
            # length = src_font_table.check_length_from_address(address)
            len_src_sentence = src_font_table.check_length_from_sentence(
                sentence=src_sentence, custom_words=custom_words
            )
            len_dst_sentence = dst_font_table.check_length_from_sentence(
                sentence=dst_sentence, custom_words=custom_words
            )
            # if len_src_sentence != len_dst_sentence:
            #     console.print(f"{address},{file_tag}", style=color)
            #     print(len(src_sentence), len(dst_sentence))
            #     assert 0, f"Sentence length is not matched. {src_sentence} != {dst_sentence}"
            #     continue

            # print(file.name, address)
            # print(src_sentence)
            # print(dst_sentence)
            translated = dictionary[src_sentence]["translated"]
            if len(translated) == 1:
                len_translated = dst_font_table.check_length_from_sentence(
                    sentence=translated[0], custom_words=custom_words
                )
                # if len_dst_sentence != len_translated:
                #     console.print(f"Length mismatch: {address},{file_tag}", style="red")
                #     continue

                if dst_script.script[address] != translated[0]:
                    dst_script.script[address] = translated[0]
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
            dst_script.save(str(dst_path))


if __name__ == "__main__":
    main()
