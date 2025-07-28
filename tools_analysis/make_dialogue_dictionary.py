import json
from pathlib import Path
from rich.console import Console
from module.font_table import FontTable


def main():
    console = Console()
    base_dir = Path("c:/work_han/workspace")
    script_dir = base_dir / "script-dos"

    dictionary = dict()

    # Read an existing dictionary
    dictionary_path = base_dir / f"rb_dictionary.json"
    annoying_path = base_dir / f"rb_annoying.json"

    # Read a pair of scripts
    for file in script_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue
        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        if not dst_path.exists():
            continue
        file_tag = f"{file.parent.name}/{file.name}"
        console.print(file_tag)
        with open(file, "r", encoding="utf-8") as f:
            src = json.load(f)
        with open(dst_path, "r", encoding="utf-8") as f:
            dst = json.load(f)

        src_font_table = FontTable("./font_table/font_table-jpn-full.json")
        dst_font_table = FontTable("./font_table/font_table-kor-jin.json")

        # check address
        for address, src_sentence in src.items():

            if "=" not in address:
                continue

            # Check if the address is in the destination script
            if address not in dst:
                continue

            # Check if the src and dst sentences are valid
            length = src_font_table.check_length_from_address(address)
            length_from_src_sentence = src_font_table.check_length_from_sentence(
                src_sentence
            )

            if length != length_from_src_sentence:
                console.print(f"{address} {file_tag}", style="red")
                assert (
                    0
                ), f"sentence length is not matched. {address}:{length} != {length_from_dst_sentence}"
                continue

            # Check if the src and dst sentences are valid
            dst_sentence = dst[address]
            length_from_dst_sentence = dst_font_table.check_length_from_sentence(
                dst_sentence
            )
            if length != length_from_dst_sentence:
                console.print(f"{address} {file_tag}", style="red")
                assert (
                    0
                ), f"sentence length is not matched. {address}:{length} != {length_from_dst_sentence}"
                continue

            count_false_character, false_character = dst_font_table.verify_sentence(
                dst_sentence
            )
            # if count_false_character:
            #     console.print(f"{address} {file_tag}", style="red")
            #     continue

            # Add the sentence to the dictionary
            if not src_sentence in dictionary:
                dictionary[src_sentence] = {
                    "count": 0,
                    "reference": 0,
                    "translated": [],
                }

            dictionary[src_sentence]["reference"] += 1
            if not dst_sentence in dictionary[src_sentence]["translated"]:
                dictionary[src_sentence]["count"] += 1
                dictionary[src_sentence]["translated"].append(dst_sentence)

    # Save a dictionary
    with open(dictionary_path, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)

    # Make an annoying dictionary - for cases that a source script has multiple destination scripts
    annoying = dict()
    for key, value in dictionary.items():
        if value["count"] > 1:
            annoying[key] = value

    print("Number of scripts = ", len(dictionary))
    print("Number of annoying scripts = ", len(annoying))

    # Save the annoying dictionary
    with open(annoying_path, "w", encoding="utf-8") as f:
        json.dump(annoying, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
