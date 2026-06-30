import json
from pathlib import Path
from rich.console import Console
from module.content import Content
from module.font_table import get_cached_font_table


def main():
    ws_num = 6
    platform = "dos"
    platform = "pc98"
    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    base_script_dir = base_dir / f"script-{platform}"
    script_path = base_script_dir / "MAIN.EXE_kor.json"
    script_path = base_script_dir / "MESSAGE.DAT_kor.json"
    script_path = base_script_dir / "DATA/ITEMDOC.TBZ_kor.json"

    custom_word_path = base_script_dir / "custom_word.json"
    custom_words = {}
    if custom_word_path.exists():
        with open(custom_word_path, "r", encoding="utf-8") as f:
            custom_words = json.load(f)

    dst_font_table = get_cached_font_table(
        file_path=Path("./font_table/font_table-kor-jin.json"),
        base_dir=base_dir,
        custom_char_path=base_script_dir / "custom_char.json",
    )

    # … ␀ ␁
    dialogue_array = {
        "016D1=016F0": "혼돈의 무수한 암흑검이 대상을_ ",
        "016F2=01705": "난도질하는 마법._ ",
    }

    console = Console()

    confirmed = False
    confirmed = True
    for script_range, dialogue in dialogue_array.items():
        dialogue = dialogue.replace(" ", "|_")
        # dialogue = dialogue.replace(" ", "_")

        dialogue_array[script_range] = dialogue
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

    if confirmed:
        if not script_path.exists():
            print(f"Script file {script_path} does not exist.")
            return
        with open(script_path, "r", encoding="utf-8") as f:
            src_script = json.load(f)

        for script_range, dialogue in dialogue_array.items():
            if script_range in src_script:
                content = Content.parse(src_script[script_range])
                content.text = dialogue
            else:
                content = Content(text=dialogue)
            src_script[script_range] = content.serialize()

        console.print("Saved", style="green")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(src_script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
