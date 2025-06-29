import json
from pathlib import Path
from rich.console import Console


def main():
    console = Console()
    base_dir = Path("c:/work_han/workspace")
    base_ref_dir = Path("c:/work_han/backup")

    out = "m234"
    if out == "m234":
        base_script_dir = base_dir
        ref = "m23"
        script_dir = base_script_dir / "m4"
    elif out == "m23":
        base_script_dir = base_ref_dir
        ref = "m2"
        script_dir = base_script_dir / "m3"
    elif out == "m2":
        base_script_dir = base_ref_dir
        script_dir = base_script_dir / "m2"
    elif out == "m3":
        base_script_dir = base_ref_dir
        script_dir = base_script_dir / "m3"
    elif out == "m4":
        base_script_dir = base_ref_dir
        script_dir = base_dir / "m4"

    if out in ["m2", "m3", "m4"]:
        dictionary = dict()
    else:
        reference_dictionary_path = base_ref_dir / f"{ref}_dictionary.json"
        with open(reference_dictionary_path, "r", encoding="utf-8") as f:
            dictionary = json.load(f)

    # Read an existing dictionary
    dictionary_path = base_ref_dir / f"{out}_dictionary.json"
    annoying_path = base_ref_dir / f"{out}_annoying.json"

    # Read a pair of scripts
    for file in script_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue
        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        if not dst_path.exists():
            continue
        file_tag = f"{file.parent.name}/{file.name}"

        with open(file, "r", encoding="utf-8") as f:
            src = json.load(f)
        with open(dst_path, "r", encoding="utf-8") as f:
            dst = json.load(f)

        # check address
        for address, src_sentence in src.items():
            if not src_sentence in dictionary:
                dictionary[src_sentence] = {
                    "count": 0,
                    "reference": 0,
                    "translated": [],
                }

            if address in dst:
                dst_sentence = dst[address]

                if "|" in dst_sentence:
                    pass
                else:
                    if len(src_sentence) != len(dst_sentence):
                        console.print(f"{address} {file_tag}", style="red")
                        assert (
                            0
                        ), f"sentence length is not matched. {address}/{len(src_sentence)} != {len(dst_sentence)}"
                        continue
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
