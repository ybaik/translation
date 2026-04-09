import json
from pathlib import Path
from rich.console import Console
from module.font_table import get_cached_font_table


def main():
    ws_num = 1
    platform = "dos"
    platform = "pc98"
    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    base_script_dir = base_dir / f"script-{platform}"
    script_path = base_script_dir / "MAIN.EXE_kor.json"
    script_path = base_script_dir / "MESSAGE.DAT_kor.json"
    # script_path = base_dir / "OPEN.EXE_kor.json"

    custom_word_path = base_script_dir / "custom_word.json"
    custom_words = {}
    if custom_word_path.exists():
        with open(custom_word_path, "r", encoding="utf-8") as f:
            custom_words = json.load(f)

    dst_font_table = get_cached_font_table(
        file_path=Path("./font_table/font_table-kor-jin.json"), base_dir=base_dir, custom_char_dir=base_script_dir
    )

    # … ␀ ␁
    dialogue_array = {
        "024E5=02512": "{다이묘} 동향을 알고 싶다고|?|␂오고 가는 정으로 돈 |␂",
        "02536=02571": "그런가,아쉽구먼._|␂오랜만에 반야탕을 |␂맛볼 수 있나 했더만|.",
    }

    console = Console()

    confirmed = False
    confirmed = True
    for script_range, dialogue in dialogue_array.items():
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

    if confirmed:
        if not script_path.exists():
            print(f"Script file {script_path} does not exist.")
            return
        with open(script_path, "r", encoding="utf-8") as f:
            src_script = json.load(f)

        for script_range, dialogue in dialogue_array.items():
            src_script[script_range] = dialogue

        console.print("Saved", style="green")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(src_script, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
