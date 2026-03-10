import json
from pathlib import Path


def main():
    base_dir = Path("c:/work_han/workspace3")
    json_path = base_dir / "europe_name.json"
    # France: 10
    # Russia: 12
    # Britain: 14
    # America: 18
    # Germany: 39
    # Miscellaneous: 6

    with open(json_path, "r", encoding="utf-8") as f:
        europe_name = json.load(f)

    role = "Miscellaneous"
    count = 0
    count_jpn = 0
    for k, v in europe_name.items():
        if v["role"] == role:
            count += 1

            if v.get("jpn") is not None:
                count_jpn += 1
            else:
                print(k)

    print(count, count_jpn)

    input_names = ["Morris", "Ottoway", "Patton", "Roberts", "Sanders", "Taylor"]
    is_updated = False
    for name in input_names:
        if name not in europe_name:
            europe_name[name] = {
                "role": role,
            }
            is_updated = True

    if is_updated:
        sorted_dict = dict(sorted(europe_name.items(), key=lambda item: item[0]))
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(sorted_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
