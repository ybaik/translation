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
        "1B589=1B5CD": "저승계|_세|_곳으로|_이루어져|_있다|.|G|X|W나는|_신들을|_모아|_지상을|_비췄고|_|C|0|0|9",
        "1B5CF=1B614": "사람들은|_평화롭게|_살고|_있었다|.|G|N그리고|_평화로운|_시간이|_흘러,지상계|C|0|1|0",
        "1B616=1B65B": "의|_사람들이|_늘어나고|_문화가|_싹트기|_시작했다.|G|X하지만|_이로|_인해|_사|C|0|1|1",
        "1B65D=1B6A2": "람들은|_지금까지보다|_더욱|_강한|_욕망을|_품게|_되었다|.|G|X지금,인간계에C|0|1|2",
    }
    # …
    dialogue_array = [
        "저승계|_세|_곳으로|_이루어져|_있다|.|G|X|W나는|_신들을|_모아|_지상을|_비췄고|_|C|0|0|9",
        "사람들은|_평화롭게|_살고|_있었다|.|G|N그| 후|_평화로운|_시간이|_흘러,지상계|C|0|1|0",
        "의|_사람들이|_늘어나고|_문화가|_싹트기|_시작했다.|G|X하지만|_이로|_인해|_사|C|0|1|1",
        "람들은|_지금까지보다|_더욱|_강한|_욕망을|_품게|_되었다|.|G|X지금,인간계에C|0|1|2",
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

    base_dir = Path("c:/work_han/workspace/script-dos")
    script_path = base_dir / "EVENT.DAT_kor.json"
    main(script_path)
