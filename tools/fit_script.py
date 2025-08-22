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
        "436A6=436C9": "祖国は危機にある|␂|␂立ち上がる時が来た",
        "436CB=436EA": "私の辞書にも|␂|␂不可能の文字はない",
        "436EC=43711": "我が国に、憂いなし|␂|␂勇猛군단あればなり",
        "43713=43738": "勇者は我につづけ!|␂|␂군인魂を見せてやる",
        "4373A=4375D": "自由と平等そして|␂|␂友愛のために戦おう",
        "4375F=4377A": "諸君を世界一の|␂|␂沃野に導こう",
        "4377C=4379F": "勝利は병사諸君の|␂|␂双肩にかかっている",
        "437A1=437C6": "硝煙の彼方に勝利の|␂|␂女神が待っているぞ",
        "437C8=437E3": "くれるものは|␂|␂もらっておこう",
        "437E5=43806": "私の価値にやっと|␂|␂気がつかれたか!",
        "43808=43825": "わが栄光は閣下と|␂|␂共にあります",
        "43827=43844": "私たちの間に|␂|␂金など無用なのに",
        "43846=43863": "わが栄光は陛下と|␂|␂共にあります",
        "43865=4387E": "この上なき|␂|␂名誉であります",
    }
    # …
    dialogue_array = {
        "436A6=436C9": "조국의 위기이다|! |␂|␂일어설 때가 왔다|!",
        "436CB=436EA": "내 사전엔__ |␂|␂불가능이란 없다|.",
        "436EC=43711": "용맹한 군단이 있어 |␂|␂우린 걱정이 없다|!",
        "43713=43738": "모두 나를 따르라|!|␂|␂군인 혼을 보여주마|!",
        "4373A=4375D": "자유와 평등,_|␂|␂우애를 위해 싸우자|!",
        "4375F=4377A": "곧 비옥한 |␂|␂땅으로 이끌겠다|!",
        "4377C=4379F": "승리는 병사들의_|␂|␂어깨에 달려 있다|!",
        "437A1=437C6": "연기 너머에 승리의|␂|␂여신이 기다린다|!_",
        "437C8=437E3": "주는 건, |␂|␂감사히 받아두지|.",
        "437E5=43806": "드디어 내 가치를|␂|␂알아본 건가|!__",
        "43808=43825": "내 영광은 |␂|␂각하와 함께합니다|!",
        "43827=43844": "우리 사이에|␂|␂돈은 필요 없는데|.",
        "43846=43863": "내 영광은 폐하와|␂|␂함께 합니다|.",
        "43865=4387E": "이보다 큰 |␂|␂영예는 없지요|.",
    }
    console = Console()

    confirmed = False
    confirmed = True

    if len(script_dict.keys()) != len(dialogue_array.values()):
        print(
            f"Script range {len(script_dict.keys())} and dialogue array length {len(dialogue_array.values())} are not matched."
        )
        return

    for script_range, dialogue in zip(script_dict.keys(), dialogue_array.values()):
        dialogue = dialogue.replace(" ", "|_")
        length = dst_font_table.check_length_from_address(script_range)
        length_from_dialogue = dst_font_table.check_length_from_sentence(dialogue)
        original_dialogue = script_dict[script_range]

        if length != length_from_dialogue:
            confirmed = False
            console.print(
                f"{length} {original_dialogue} {dialogue} {length_from_dialogue - length}",
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
    base_dir = Path("c:/work_han/workspace3/script-pc98")
    script_path = base_dir / "MAIN.EXE_kor.json"
    main(script_path)
