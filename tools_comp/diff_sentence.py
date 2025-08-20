import json
from pathlib import Path


def read_script(path):
    with open(path, "r", encoding="utf-8") as f:
        script = json.load(f)
    script.pop("custom_codes", None)
    script.pop("custom_input", None)
    return script


def check_diff_and_save(script, shared_set, save_path):
    script_diff = {}
    for address, sentence in script.items():
        if "=" not in address:
            continue
        if sentence in shared_set:
            continue
        script_diff[address] = sentence

    if len(script_diff):
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(script_diff, f, ensure_ascii=False, indent=4)


def main():
    base_dir = Path("c:/work_han/workspace")
    src_dir = base_dir / "script-dos"
    dst_dir = base_dir / "script-pc98"

    for file in src_dir.glob("*.json"):  # Use rglob to search subdirectories
        if "diff" in file.name:
            continue

        # Check same file in dst
        dst_file = dst_dir / file.name
        if not dst_file.exists():
            continue

        src_script = read_script(src_dir / file.name)
        dst_script = read_script(dst_dir / file.name)
        sv = set(src_script.values())
        dv = set(dst_script.values())

        shared_set = sv.intersection(dv)

        save_file_name = file.name.replace(".json", "_diff.json")
        check_diff_and_save(src_script, shared_set, src_dir / save_file_name)
        check_diff_and_save(dst_script, shared_set, dst_dir / save_file_name)


if __name__ == "__main__":
    main()
