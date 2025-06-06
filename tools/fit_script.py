import json
from pathlib import Path
from rich.console import Console


def main(script_path: Path):

    if not script_path.exists():
        print(f"Script file {script_path} does not exist.")
        return
    with open(script_path, "r", encoding="utf-8") as f:
        src_script = json.load(f)

    script_dict = {"0095D=00974": "とっても似合うと思うよ。"}
    # …
    dialogue_array = ["정말 잘 어올려 보여."]

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
        console.print("[green] Saved [/green]")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(src_script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    base_dir = Path("c:/work_han/workspace/script")
    script_path = base_dir / "H02_ADV.BIN_kor.json"
    main(script_path)
