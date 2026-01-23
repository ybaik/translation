import os
import cv2
import json
import numpy as np
from PIL import Image
from pathlib import Path
from module.name_db import NameDB
from module.font_table import FontTable
from module.font_image import imread_korean, draw_letters_on_canvas


def imread_korean(path):
    img_array = np.fromfile(path, np.uint8)
    img = cv2.imdecode(img_array, 0)
    return img


def set_4byte(base_dir: Path, base_name_db_dir: Path, font_table: FontTable, src_font_canvas: np.ndarray):
    start_code = "959F"  # 福
    input_cand_4byte = ["다이묘"]

    with open(base_name_db_dir / "region_db.json", "r", encoding="utf-8") as f:
        region_db = json.load(f)

    # Select regions that has more than 4 Korean letters
    for korean in region_db.values():
        if len(korean) >= 3:
            input_cand_4byte.append(korean)

    # Read 4byte image information
    img_db_4byte = {}
    for letter_path in (base_dir / "byte4").rglob("*.bmp"):
        img_db_4byte[letter_path.stem] = letter_path

    # Check if the image file exists
    for korean in input_cand_4byte:
        if korean not in img_db_4byte:
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


def set_6byte(base_dir: Path, base_name_db_dir: Path, font_table: FontTable, src_font_canvas: np.ndarray):
    start_code = "9640"  # 法
    game = "nb4"

    name_db = NameDB()
    input_cand_6byte = []

    # Select regions that has more than 4 Korean letters
    for db in name_db.full_name_db.values():
        if game not in db["game"]:
            continue
        fname, gname = db["kor"].split(" ")
        if len(fname) >= 4 and fname not in input_cand_6byte:
            input_cand_6byte.append(fname)
        if len(gname) >= 4 and gname not in input_cand_6byte:
            input_cand_6byte.append(gname)

    # Read 6byte image information
    img_db_6byte = {}
    for letter_path in (base_dir / "byte6").rglob("*.bmp"):
        img_db_6byte[letter_path.stem] = letter_path
    img_db_3byte = {}
    for letter_path in (base_dir / "byte3").rglob("*.bmp"):
        img_db_3byte[letter_path.stem] = letter_path

    # Check if the image file exists
    for korean in input_cand_6byte:
        if korean in img_db_6byte:
            continue
        # Try to make a 6byte image if korean is 4 letters
        if len(korean) == 4:
            if korean[:2] in img_db_3byte and korean[2:] in img_db_3byte:
                sav_path = base_dir / "byte6" / f"{korean}.bmp"

                img1 = imread_korean(str(img_db_3byte[korean[:2]]))
                img2 = imread_korean(str(img_db_3byte[korean[2:]]))
                h_img = cv2.hconcat([img1, img2])
                pil_img = Image.fromarray(h_img)
                one_bit_img = pil_img.convert("1")
                one_bit_img.save(sav_path)
                img_db_6byte[korean] = sav_path

    # Get filtered list
    code_list = list(font_table.code2char.keys())
    code_idx = code_list.index(start_code)
    code_list = code_list[code_idx:]

    return draw_letters_on_canvas(
        font_canvas=src_font_canvas,
        input_cands=input_cand_6byte,
        img_path_dict=img_db_6byte,
        code_list=code_list,
        num_letters=3,
    )


def main():
    base_dir = Path("c:/work_han/font_update_db")
    base_name_db_dir = Path("c:/work_han/translation/name_db")

    font_table = FontTable("font_table/font_table-jpn-full.json")
    src_font_canvas_path = base_dir / "ThinDungGeunMo.bmp"
    src_font_canvas = cv2.imread(str(src_font_canvas_path), cv2.IMREAD_GRAYSCALE)

    ret_code_dict = {}

    # Set 2byte letters

    # set 4byte letters
    ret_code_dict |= set_4byte(base_dir, base_name_db_dir, font_table, src_font_canvas)

    # set 6byte letters
    ret_code_dict |= set_6byte(base_dir, base_name_db_dir, font_table, src_font_canvas)

    # Save font canvas image
    dst_font_canvas_path = base_dir / "ThinDungGeunMo-mod.bmp"
    pil_img = Image.fromarray(src_font_canvas)
    one_bit_img = pil_img.convert("1")
    one_bit_img.save(dst_font_canvas_path)
    with open(base_dir / "code.json", "w", encoding="utf-8") as f:
        json.dump(ret_code_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
