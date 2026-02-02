import cv2
import json
import numpy as np
from PIL import Image
from pathlib import Path
from module.name_db import NameDB
from module.font_table import FontTable
from module.font_image import draw_letters_on_canvas


def set_4byte(base_dir: Path, font_table: FontTable, src_font_canvas: np.ndarray):
    start_code = "9540"  # 鼻
    input_cand_4byte = []

    input_cand_4byte.append(["다이묘", "비스코"])
    input_cand_4byte.append(["와-과", "비스코"])
    input_cand_4byte.append(["은-는", "비스코"])
    input_cand_4byte.append(["을-를", "비스코"])
    input_cand_4byte.append(["이-가", "비스코"])

    # Read 4byte image information
    img_db_4byte = dict()

    for korean, font_name in input_cand_4byte:
        if font_name in img_db_4byte:
            continue
        img_db_4byte[font_name] = dict()
        font_dir = "byte4" if font_name == "default" else f"byte4{font_name}"
        for letter_path in (base_dir / font_dir).rglob("*.bmp"):
            img_db_4byte[font_name][letter_path.stem] = letter_path

    # Check if the image file exists
    for korean, font_name in input_cand_4byte:
        if korean not in img_db_4byte[font_name]:
            print(f"{korean} - no font")

    # Get filtered list
    code_list = list(font_table.code2char.keys())
    code_idx = code_list.index(start_code)
    code_list = code_list[code_idx:]

    return draw_letters_on_canvas(
        font_canvas=src_font_canvas,
        input_cands=input_cand_4byte,
        img_path_dict=img_db_4byte,
        code_list=code_list,
        num_letters=2,
    )


def set_2byte(base_dir: Path, input_cand_2byte: list, font_table: FontTable, src_font_canvas: np.ndarray):
    start_code = "959F"  # 福

    # Read 4byte image information
    img_db_1byte = {
        "default": dict(),
    }
    for letter_path in (base_dir / "byte1").rglob("*.bmp"):
        img_db_1byte["default"][letter_path.stem] = letter_path

    # Get filtered list
    code_list = list(font_table.code2char.keys())
    code_idx = code_list.index(start_code)
    code_list = code_list[code_idx:]

    return draw_letters_on_canvas(
        font_canvas=src_font_canvas,
        input_cands=input_cand_2byte,
        img_path_dict=img_db_1byte,
        code_list=code_list,
        num_letters=1,
        need_merge=True,
    )


def split_and_pair(text: str, pairs: set) -> None:
    space = False
    for i in range(0, len(text), 2):
        pair = text[i : i + 2]

        if " " in pair:
            space = True

        # 길이가 1이면 뒤에 "_" 추가
        if len(pair) == 1:
            pair += "_"
        pairs.add(pair)
    return space


def main():
    base_dir = Path("c:/work_han/font_update_db")
    db_dir = Path("C:/work_han/translation/name_db")

    font_table = FontTable(Path("font_table/font_table-jpn-full.json"))
    src_font_canvas_path = base_dir / "BISCO.bmp"
    src_font_canvas = cv2.imread(str(src_font_canvas_path), cv2.IMREAD_GRAYSCALE)

    letter_2byte = set()

    # Name
    db = NameDB()
    for jpn, data in db.full_name_db.items():
        if "game" not in data:
            assert 0, f"Game tag is not in the name database - {jpn}."
        if "kor" not in data:
            assert 0, f"Kor tag is not in the name database - {jpn}."
        if "nb4" not in data["game"]:
            continue
        kors = data["kor"]
        for kor in kors.split(" "):
            space = split_and_pair(kor, letter_2byte)
            if space:
                print(1)

    # Region
    with open(db_dir / "region_db.json", "r", encoding="utf-8") as f:
        region_db = json.load(f)
        for v in region_db.values():
            space = split_and_pair(v, letter_2byte)
            if space:
                print(1)

    # Mountain, etc.
    with open(db_dir / "nb4" / "nb4_산천성.json", "r", encoding="utf-8") as f:
        san_db = json.load(f)
        for v in san_db.values():
            text = v["kor"]
            if text[-1] == "산":
                text = text[:-1]
            if text[-2:] == "산성":
                text = text[:-2]
            space = split_and_pair(text, letter_2byte)
            if space:
                print(1)

    # 다기
    with open(db_dir / "nb4" / "nb4_다기.json", "r", encoding="utf-8") as f:
        san_db = json.load(f)
        for k, v in san_db.items():
            kor = v["kor"].replace(" ", "")
            space = split_and_pair(kor, letter_2byte)
            if space:
                print(1)

    letter_2byte = list(letter_2byte)
    letter_2byte.sort()
    print(len(letter_2byte))
    # print(letter_2byte)

    ret_code_dict = {}

    # set 4byte letters
    ret_code_dict |= set_4byte(base_dir, font_table, src_font_canvas)

    # Set 2byte letters
    letter_2byte = [[s, "default"] for s in letter_2byte]  # Change format
    ret_code_dict |= set_2byte(base_dir, letter_2byte, font_table, src_font_canvas)

    # Save font canvas image
    dst_font_canvas_path = base_dir / "nobu4-BISCO.bmp"
    pil_img = Image.fromarray(src_font_canvas)
    one_bit_img = pil_img.convert("1")
    one_bit_img.save(dst_font_canvas_path)
    with open(base_dir / "code.json", "w", encoding="utf-8") as f:
        json.dump(ret_code_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
