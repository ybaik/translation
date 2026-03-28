import cv2
import json
import numpy as np
from PIL import Image
from pathlib import Path
from module.name_db import NameDB
from module.font_table import FontTable
from module.font_image import draw_letters_on_canvas


def set_font(
    base_dir: Path,
    font_table: FontTable,
    src_font_canvas: np.ndarray,
    start_code: str,
    num_letters: int,
    input_cands: list,
):
    # Read image information
    img_db = dict()

    num_bytes = num_letters * 2

    for korean, font_name in input_cands:
        if font_name in img_db:
            continue
        img_db[font_name] = dict()
        font_dir = f"byte{num_bytes}" if font_name == "default" else f"byte{num_bytes}{font_name}"
        for letter_path in (base_dir / font_dir).rglob("*.bmp"):
            img_db[font_name][letter_path.stem] = letter_path

    # Check if the image file exists
    for korean, font_name in input_cands:
        if korean not in img_db[font_name]:
            print(f"{korean} - no font")

    # Get filtered list
    code_list = list(font_table.code2char.keys())
    code_idx = code_list.index(start_code)
    code_list = code_list[code_idx:]

    ret_dict_code, next_code_idx = draw_letters_on_canvas(
        font_canvas=src_font_canvas,
        input_cands=input_cands,
        img_path_dict=img_db,
        code_list=code_list,
        num_letters=num_letters,
    )

    next_code = code_list[next_code_idx]

    return ret_dict_code, next_code


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

    ret_dict_code, code_idx = draw_letters_on_canvas(
        font_canvas=src_font_canvas,
        input_cands=input_cand_4byte,
        img_path_dict=img_db_4byte,
        code_list=code_list,
        num_letters=2,
    )

    return ret_dict_code


def set_2byte_merge(base_dir: Path, input_cand_2byte: list, font_table: FontTable, src_font_canvas: np.ndarray):
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

    ret_dict_code, code_idx = draw_letters_on_canvas(
        font_canvas=src_font_canvas,
        input_cands=input_cand_2byte,
        img_path_dict=img_db_1byte,
        code_list=code_list,
        num_letters=1,
        need_merge=True,
    )

    print(f"Final code: {code_list[code_idx]}")
    return ret_dict_code


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
    font_name = "비스코"  # "둥근모", "비스코"
    if font_name == "둥근모":
        font_file = "ThinDungGeunMo.bmp"
    if font_name == "비스코":
        font_file = "BISCO.bmp"

    font_table = FontTable(Path("font_table/font_table-jpn-full.json"))
    src_font_canvas_path = base_dir / font_file
    src_font_canvas = cv2.imread(str(src_font_canvas_path), cv2.IMREAD_GRAYSCALE)

    letter_2byte = set()

    # Name
    fset = set()
    gset = set()
    db = NameDB()
    for jpn, data in db.full_name_db.items():
        if "game" not in data:
            assert 0, f"Game tag is not in the name database - {jpn}."
        if "kor" not in data:
            assert 0, f"Kor tag is not in the name database - {jpn}."
        if "taiko2" not in data["game"]:
            continue
        kors = data["kor"]

        family_name, given_name = kors.split(" ")
        if len(family_name) > 6 or len(given_name) > 6:
            print(kors)
            continue

        fa = False
        ga = False
        if len(family_name) % 2:
            family_name += "_"
            fa = True
        if len(given_name) % 2:
            given_name = "_" + given_name
            ga = True

        # if fa and ga:
        #     print(kors)
        #     fset.add(family_name[-2])
        #     gset.add(given_name[-1])

        split_and_pair(family_name, letter_2byte)
        split_and_pair(given_name, letter_2byte)

    # print(len(fset), len(gset))
    # print(fset)
    # print(gset)
    letter_2byte = list(letter_2byte)

    # 추가
    letter_2byte.append("사노")

    letter_2byte.sort()
    print(len(letter_2byte))

    ret_code_dict = {}
    start_code = "9540"  # 鼻
    input_cand = []
    input_cand.append(["은", "비스코"])
    input_cand.append(["는", "비스코"])
    input_cand.append(["이", "비스코"])
    input_cand.append(["가", "비스코"])
    input_cand.append(["을", "비스코"])
    input_cand.append(["를", "비스코"])
    input_cand.append(["와", "비스코"])
    input_cand.append(["과", "비스코"])
    input_cand.append(["에", "비스코"])
    input_cand.append(["의", "비스코"])
    code_dict, next_code = set_font(base_dir, font_table, src_font_canvas, start_code, 1, input_cand)
    ret_code_dict |= code_dict

    # set 4byte letters
    input_cand = []
    input_cand.append(["다이묘", font_name])
    input_cand.append(["와-과", font_name])
    input_cand.append(["은-는", font_name])
    input_cand.append(["을-를", font_name])
    input_cand.append(["이-가", font_name])

    input_cand.append(["도토미", font_name])
    input_cand.append(["무사시", "둥근모"])
    input_cand.append(["미카와", font_name])
    input_cand.append(["사가미", font_name])
    input_cand.append(["사누키", "둥근모"])
    input_cand.append(["사츠마", font_name])
    input_cand.append(["스루가", "둥근모"])
    input_cand.append(["시나노", "둥근모"])
    input_cand.append(["시모사", "둥근모"])
    input_cand.append(["야마토", "둥근모"])
    input_cand.append(["에치고", font_name])
    input_cand.append(["에치젠", font_name])
    input_cand.append(["오와리", "둥근모"])
    input_cand.append(["이나바", "둥근모"])
    input_cand.append(["이와미", "둥근모"])
    input_cand.append(["이즈모", font_name])
    input_cand.append(["코즈케", "둥근모"])
    input_cand.append(["하리마", font_name])
    input_cand.append(["히타치", font_name])

    code_dict, next_code = set_font(base_dir, font_table, src_font_canvas, next_code, 2, input_cand)
    ret_code_dict |= code_dict

    # Set merged 2byte letters
    letter_2byte = [[s, "default"] for s in letter_2byte]  # Change format
    ret_code_dict |= set_2byte_merge(base_dir, letter_2byte, font_table, src_font_canvas)

    # Save font canvas image
    dst_font_canvas_path = base_dir / f"taikou2-{font_file}"
    pil_img = Image.fromarray(src_font_canvas)
    one_bit_img = pil_img.convert("1")
    one_bit_img.save(dst_font_canvas_path)
    with open(base_dir / "code.json", "w", encoding="utf-8") as f:
        json.dump(ret_code_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
