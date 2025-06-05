import json
from pathlib import Path
from rich.console import Console


def main(script_path: Path):

    if not script_path.exists():
        print(f"Script file {script_path} does not exist.")
        return
    with open(script_path, "r") as f:
        src_script = json.load(f)

    script_dict = {
        "7A=AB": "これから始まるシナリオは、スタッフのお遊びですので",
        "AF=E0": "氣にせず樂しんで下さい。なお、このシナリオに關する",
        "E4=115": "質問はユ-ザ-サポ-ト係では、受け付けておりません",
        "8C3=8D0": "おしまいだよ☆",
    }
    # …
    dialogue_array = [
        "이제 시작될 시나리오는,스태프의 장난이므로  ",
        "신경쓰지 말고 즐겨주세요.이 시나리오에 관한 ",
        "질문은 사용자 지원 부서에서 받지 않습니다. ",
        "끝이야☆   ",
    ]

    console = Console()

    confirmed = False
    confirmed = True

    if len(script_dict.keys()) != len(dialogue_array):
        print(
            f"Script range {len(script_dict.keys())} and dialogue array length {len(dialogue_array)} are not matched."
        )
        return

    for script_range, dialogue in zip(script_dict.keys(), dialogue_array):
        dialogue = dialogue.replace(" ", "_")
        length = len(dialogue)
        codes = script_range.split("=")
        s_code_int = int(codes[0], 16)
        e_code_int = int(codes[1], 16)
        l_len = (e_code_int - s_code_int + 1) // 2

        original_dialogue = script_dict[script_range]

        if l_len != length:
            confirmed = False
            console.print(
                f"[yellow]{l_len} {original_dialogue} {dialogue} {length - l_len}[/yellow]"
            )
        else:
            print(l_len, original_dialogue, dialogue, length - l_len)
            src_script[script_range] = dialogue

    if confirmed:
        with open(script_path, "w") as f:
            json.dump(src_script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    base_dir = Path("c:/work_han/workspace")
    script_path = base_dir / "SPC4_VIS.BIN_kor.json"
    main(script_path)
