import cv2
import json
import numpy as np
from PIL import Image
from pathlib import Path
from module.font_table import FontTable
from module.font_image import draw_letters_on_canvas


def set_8byte(base_dir: Path, font_name: str, font_table: FontTable, src_font_canvas: np.ndarray):
    start_code = "959F"  # 福
    input_cand_8byte = []

    input_cand_8byte.append(["로트미스트로프", font_name])
    input_cand_8byte.append(["바이언라인", font_name])
    input_cand_8byte.append(["로코소프스키", font_name])
    input_cand_8byte.append(["슈베펜부르크", font_name])
    input_cand_8byte.append(["에이브람스", font_name])
    input_cand_8byte.append(["비스마르크", font_name])
    input_cand_8byte.append(["브뤼노비치", font_name])
    input_cand_8byte.append(["아이젠하워", font_name])
    input_cand_8byte.append(["프라이버그", font_name])
    input_cand_8byte.append(["클라이스트", font_name])
    input_cand_8byte.append(["라펜슈타인", font_name])
    input_cand_8byte.append(["라이헤나우", font_name])
    input_cand_8byte.append(["룬트슈테트", font_name])
    input_cand_8byte.append(["스코르체니", font_name])
    input_cand_8byte.append(["바실렙스키", font_name])

    # Read 8byte image information
    img_db_8byte = dict()

    for korean, font_name in input_cand_8byte:
        if font_name in img_db_8byte:
            continue
        img_db_8byte[font_name] = dict()
        font_dir = "byte8" if font_name == "default" else f"byte8{font_name}"
        for letter_path in (base_dir / font_dir).rglob("*.bmp"):
            img_db_8byte[font_name][letter_path.stem] = letter_path

    # Check if the image file exists
    for korean, font_name in input_cand_8byte:
        if korean not in img_db_8byte[font_name]:
            print(f"{korean} - no font")

    # Get filtered list
    code_list = list(font_table.code2char.keys())
    code_idx = code_list.index(start_code)
    code_list = code_list[code_idx:]

    return draw_letters_on_canvas(
        font_canvas=src_font_canvas,
        input_cands=input_cand_8byte,
        img_path_dict=img_db_8byte,
        code_list=code_list,
        num_letters=4,
    )


def set_2byte(base_dir: Path, input_cand_2byte: list, font_table: FontTable, src_font_canvas: np.ndarray):
    start_code = "9540"  # 鼻

    # Read 1byte image information
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
    font_table = FontTable(Path("font_table/font_table-jpn-full.json"))

    font_name = "둥근모"  # "비스코, 둥근모"

    if font_name == "비스코":
        src_font_canvas_path = base_dir / "BISCO.bmp"
        dst_font_canvas_path = base_dir / "europe-BISCO.bmp"
    elif font_name == "둥근모":
        src_font_canvas_path = base_dir / "ThinDungGeunMo.bmp"
        dst_font_canvas_path = base_dir / "europe-ThinDungGeunMo.bmp"
    else:
        assert 0, f"Font name is not supported - {font_name}."

    src_font_canvas = cv2.imread(str(src_font_canvas_path), cv2.IMREAD_GRAYSCALE)

    letter_2byte = set()
    # Add custom word
    letter_2byte.add("맑음")
    letter_2byte.add("흐림")
    letter_2byte.add("안개")
    letter_2byte.add("폭풍")
    letter_2byte = list(letter_2byte)
    letter_2byte.sort()
    print(len(letter_2byte))

    ret_code_dict = {}
    # Set 2byte letters
    letter_2byte = [[s, "default"] for s in letter_2byte]  # Change format
    ret_code_dict |= set_2byte(base_dir, letter_2byte, font_table, src_font_canvas)

    # set 8byte letters
    ret_code_dict |= set_8byte(base_dir, font_name, font_table, src_font_canvas)

    # Save font canvas image

    pil_img = Image.fromarray(src_font_canvas)
    one_bit_img = pil_img.convert("1")
    one_bit_img.save(dst_font_canvas_path)
    with open(base_dir / "code.json", "w", encoding="utf-8") as f:
        json.dump(ret_code_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
