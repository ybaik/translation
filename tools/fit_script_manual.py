import json
from pathlib import Path
from rich.console import Console


def main():

    script_dict = {
        "0080B=00826": "そういえば、輝さんに会うの、",
        "0082A=00839": "あれ以来ですね？",
    }
    # …
    dialogue_array = ["그런데,히카루씨를 만나는건", "그후 처음이죠?"]

    console = Console()

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
            console.print(
                f"[yellow]{l_len} {original_dialogue} {dialogue} {length - l_len}[/yellow]"
            )
        else:
            print(l_len, original_dialogue, dialogue, length - l_len)


if __name__ == "__main__":
    main()
