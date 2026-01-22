import json
from pathlib import Path
from rich.console import Console
from module.font_table import FontTable


def main():
    ws_num = 4
    base_dir = Path(f"c:/work_han/workspace{ws_num}/script-pc98")
    # script_path = base_dir / "EVENT.DAT_kor.json"
    script_path = base_dir / "MAIN.EXE_kor.json"

    if not script_path.exists():
        print(f"Script file {script_path} does not exist.")
        return
    with open(script_path, "r", encoding="utf-8") as f:
        src_script = json.load(f)

    dst_font_table = FontTable("./font_table/font_table-kor-jin.json")

    # … ␀ ␁
    dialogue_array = {
        "2B07E=2B095": "금을 얼마나 소지 할까요|␀",
        "2B099=2B0B2": "병량을 얼마나 소지 할까요|␀",
        "2B0B4=2B0C1": "이동할까요␀␀",
    }
    console = Console()

    confirmed = False
    confirmed = True

    for script_range, dialogue in zip(dialogue_array.keys(), dialogue_array.values()):
        dialogue = dialogue.replace(" ", "|_")
        # dialogue = dialogue.replace(" ", "_")
        length = dst_font_table.check_length_from_address(script_range)
        length_from_dialogue = dst_font_table.check_length_from_sentence(dialogue)

        if length != length_from_dialogue:
            confirmed = False
            console.print(
                f"{length} {dialogue} {length_from_dialogue - length}",
                style="yellow",
            )
        else:
            print(length, dialogue, length_from_dialogue - length)
            src_script[script_range] = dialogue

    if confirmed:
        console.print("Saved", style="green")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(src_script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
