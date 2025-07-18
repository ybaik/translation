import json
from pathlib import Path
from rich.console import Console
from module.font_table import FontTable


def main(script_path: Path):

    if not script_path.exists():
        print(f"Script file {script_path} does not exist.")
        return
    with open(script_path, "r", encoding="utf-8") as f:
        src_script = json.load(f)

    dst_font_table = FontTable("./font_table/font_table-kor-jin.json")

    script_dict = {
        "2BBFA=2BC0F": "特殊な力を持つ人たちが",
        "2BC11=2BC24": "味方になってくれれば",
        "2BC26=2BC35": "とても心強いわね",
    }
    # …
    dialogue_array = [
        "특별한| 힘을| 가진| 자가|_",
        "아군이| 되어만| 준다면",
        "정말| 든든할텐데|.",
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
        length = dst_font_table.check_length_from_address(script_range)
        length_from_dialogue = dst_font_table.check_length_from_sentence(dialogue)
        original_dialogue = script_dict[script_range]

        if length != length_from_dialogue:
            confirmed = False
            console.print(
                f"{length} {original_dialogue} {dialogue} {length_from_dialogue-length}",
                style="yellow",
            )
        else:
            print(length, original_dialogue, dialogue, length_from_dialogue - length)
            src_script[script_range] = dialogue

    if confirmed:
        console.print("Saved", style="green")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(src_script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    base_dir = Path("c:/work_han/workspace/script")
    script_path = base_dir / "MAIN.EXE_kor.json"
    main(script_path)
