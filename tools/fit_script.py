import json
from pathlib import Path


def main(script_path: Path):

    with open(script_path, "r") as f:
        src_script = json.load(f)

    script_range = [
        "1DF7=1E12",
        "1E16=1E21",
        "1E2C=1E45",
        "1E49=1E58",
        "1E63=1E78",
        "1E7C=1E93",
        "1E9E=1EB7",
        "1EBB=1ED4",
        "1EDF=1EFC",
        "1F00=1F09",
    ]

    # …
    script = "\
그래서,아버지랑 어머니도\
이렇게 말씀하셨어.\
오빠가가 얼마나 고생했는지\
알고나 있는거냐!\
말을 듣지 않으면\
부모자식 인연을 끊겠다!!\
그래서 이렇게 말했어.\
오랜시간 신세졌습니다.\
나는 반드시 가수가 될 겁니다!!\
라고……\
"

    confirmed = False
    # confirmed = True

    script = script.replace(" ", "_")
    length = len(script)
    start = 0
    for line in script_range:
        codes = line.split("=")
        s_code_int = int(codes[0], 16)
        e_code_int = int(codes[1], 16)
        l_len = (e_code_int - s_code_int + 1) // 2

        if start + l_len <= length:
            dialogue = script[start : start + l_len]
        else:
            dialogue = script[start:]
        print(l_len, dialogue)
        src_script[line] = dialogue
        start += l_len
    print(length - start)

    if confirmed and length - start == 0:
        with open(script_path, "w") as f:
            json.dump(src_script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    base_dir = Path("c:/work_han/workspace")
    script_path = base_dir / "S06_VIS_kor.json"
    main(script_path)
