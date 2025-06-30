import json
from pathlib import Path
from rich.console import Console


def main():
    console = Console()

    base_dir = Path("c:/work_han/workspace")
    ref_base_dir = Path("c:/work_han/backup")

    script_base_dir = base_dir / "m4_script"
    script_base_dir = base_dir / "m4"
    script_base_dir = base_dir
    # script_base_dir = Path("c:/work_han/backup")

    ref = "m234"
    # Read an existing dictionary
    dictionary_path = ref_base_dir / f"{ref}_dictionary.json"
    if not dictionary_path.exists():
        return
    with open(dictionary_path, "r", encoding="utf-8") as f:
        dictionary = json.load(f)

    # Read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue
        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        if not dst_path.exists():
            continue

        file_tag = f"{file.parent.name}/{file.name}"
        color = "green"
        if "m2" in file_tag:
            color = "yellow"
        elif "m3" in file_tag:
            color = "red"

        with open(file, "r", encoding="utf-8") as f:
            src = json.load(f)
        with open(dst_path, "r", encoding="utf-8") as f:
            dst = json.load(f)

        # Check addresses in the source script
        modified = False
        for address, src_sentence in src.items():
            if not src_sentence in dictionary:
                continue

            if address in dst:
                dst_sentence = dst[address]

                if "|" in dst_sentence:
                    pass
                else:
                    if len(src_sentence) != len(dst_sentence):
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
                    if len(dst[address]) != len(translated[0]):
                        console.print(
                            f"Length mismatch: {address},{file_tag}", style="red"
                        )
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
