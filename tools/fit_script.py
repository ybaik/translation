import json
from pathlib import Path
from rich.console import Console
from module.font_table import FontTable


def main():
    ws_num = 3
    base_dir = Path(f"c:/work_han/workspace{ws_num}/script-pc98")
    # script_path = base_dir / "EVENT.DAT_kor.json"
    script_path = base_dir / "MAIN.EXE_kor.json"
    script_path = base_dir / "OPENEND.EXE_kor.json"

    custom_word_path = base_dir / "custom_word.json"
    custom_words = {}
    if custom_word_path.exists():
        with open(custom_word_path, "r", encoding="utf-8") as f:
            custom_words = json.load(f)

    if not script_path.exists():
        print(f"Script file {script_path} does not exist.")
        return
    with open(script_path, "r", encoding="utf-8") as f:
        src_script = json.load(f)

    dst_font_table = FontTable(file_path=Path("./font_table/font_table-kor-jin.json"), custom_char_dir=base_dir)

    # … ␀ ␁
    dialogue_array = {
        "07133=07145": "浅井長政|(|1|5|4|5|-|1|5|7|3|)",
        "07147=0715E": "琵琶湖の辺の新興勢力。義",
        "07160=07177": "兄・織田信長の猛攻に、朝",
        "07179=0718E": "倉との共闘で対抗する。",
    }
    console = Console()

    confirmed = False
    confirmed = True

    for script_range, dialogue in zip(dialogue_array.keys(), dialogue_array.values()):
        dialogue = dialogue.replace(" ", "|_")
        # dialogue = dialogue.replace(" ", "_")
        length = dst_font_table.check_length_from_address(script_range)
        length_from_dialogue = dst_font_table.check_length_from_sentence(sentence=dialogue, custom_words=custom_words)

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
