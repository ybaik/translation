import json
from pathlib import Path
from rich.console import Console


def main():
    console = Console()

    base_dir = Path("c:/work_han/workspace")
    ref_base_dir = Path("c:/work_han/backup")

    ref = "m234"
    script_base_dir = base_dir / "script"
    # script_base_dir = base_dir / "m4"
    # script_base_dir = Path("c:/work_han/backup")

    # Read an existing dictionary
    annoying_path = ref_base_dir / f"{ref}_annoying.json"
    # annoying_path = base_dir / f"{ref}_dictionary.json"
    if not annoying_path:
        return
    with open(annoying_path, "r", encoding="utf-8") as f:
        annoying = json.load(f)

    print(f"Number of annoying scripts = {len(annoying)}")

    # Read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue

        file_tag = f"{file.parent.name}/{file.name}"
        color = "green"
        if "m2" in file_tag:
            color = "yellow"
        elif "m3" in file_tag:
            color = "red"

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
            if not src_sentence in annoying:
                continue

            if address in dst:
                dst_sentence = dst[address]
                if len(src_sentence) != len(dst_sentence):
                    console.print(f"{address},{file_tag}", style=color)
                    assert (
                        0
                    ), f"sentence length is not matched. {src_sentence} != {dst_sentence}"
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

                if "modify" in annoying[src_sentence]:
                    idx = annoying[src_sentence]["modify"]
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
