import cv2
import json
import numpy as np
from PIL import Image
from pathlib import Path
from module.name_db import NameDB
from module.font_table import FontTable
from module.font_image import draw_letters_on_canvas, return_img_roi_1byte, imread_korean


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

    return ret_dict_code


def split_and_pair(text: str, pairs: set) -> bool:
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
    font_name = "둥근모"  # "둥근모", "비스코"
    if font_name == "둥근모":
        font_file = "ThinDungGeunMo.bmp"
    if font_name == "비스코":
        font_file = "BISCO.bmp"

    font_table = FontTable(Path("font_table/font_table-jpn-full.json"))
    src_font_canvas_path = base_dir / font_file
    src_font_canvas = cv2.imread(str(src_font_canvas_path), cv2.IMREAD_GRAYSCALE)

    # 1byte font
    input_cand_1byte = []
    input_cand_1byte += ["|가", "|간", "|게", "|겐", "|고", "|기"]
    input_cand_1byte += ["|나", "|노", "|누", "|니"]
    input_cand_1byte += ["|다", "|도"]
    input_cand_1byte += ["|라", "|란", "|로", "|리"]
    input_cand_1byte += ["|마", "|무", "|미"]
    input_cand_1byte += ["|바", "|반", "|보", "|부"]
    input_cand_1byte += ["|사", "|세", "|소", "|쇼", "|슈", "|시", "|신"]
    input_cand_1byte += ["|아", "|야", "|에", "|오", "|와", "|우", "|유", "|이", "|인", "|잇"]
    input_cand_1byte += ["|조", "|죠", "|쥬", "|쥰", "|즈", "|지", "|츠", "|치"]
    input_cand_1byte += ["|카", "|칸", "|케", "|코", "|쿠", "|타", "|테", "|토"]
    input_cand_1byte += ["|한", "|호"]
    input_cand_1byte.sort()
    if len(input_cand_1byte) > 58:
        print(len(input_cand_1byte))
        return

    input_cand_1byte = []  # Remove 1byte code due to taikou1 font issue

    start_code_int = 0xA6
    ret_code_dict = {letter: f"{start_code_int + i:02X}" for i, letter in enumerate(input_cand_1byte)}

    for i, letter in enumerate(input_cand_1byte):
        roi = return_img_roi_1byte(hex(start_code_int + i))
        font_path = base_dir / "byte1" / f"{letter.replace('|', '')}.bmp"
        if not font_path.exists():
            print(f"{font_path} does not exist.")
            continue
        kor_font = imread_korean(font_path)
        src_font_canvas[roi[0] : roi[1], roi[2] : roi[3]] = kor_font

    letter_2byte = set()

    # Name
    db = NameDB()
    for jpn, data in db.full_name_db.items():
        if "game" not in data:
            assert 0, f"Game tag is not in the name database - {jpn}."
        if "kor" not in data:
            assert 0, f"Kor tag is not in the name database - {jpn}."
        if "taiko1" not in data["game"]:
            continue
        kors = data["kor"]

        family_name, given_name = kors.split(" ")
        if len(family_name) > 6 or len(given_name) > 6:
            print(kors)
            continue

        if len(family_name) % 2:
            family_name += "_"
        if len(given_name) % 2:
            given_name = "_" + given_name

        split_and_pair(family_name, letter_2byte)
        split_and_pair(given_name, letter_2byte)

    # Add
    letter_2byte.add("_마")
    letter_2byte.add("_산")
    letter_2byte.add("_소")
    letter_2byte.add("_에")
    letter_2byte.add("_텐")
    letter_2byte.add("가사")
    letter_2byte.add("가타")
    letter_2byte.add("고사")
    letter_2byte.add("고에")
    letter_2byte.add("고자")
    letter_2byte.add("고헤")
    letter_2byte.add("구니")
    letter_2byte.add("구죠")
    letter_2byte.add("기리")
    letter_2byte.add("기마")
    letter_2byte.add("나나")
    letter_2byte.add("나에")
    letter_2byte.add("나와")
    letter_2byte.add("난코")
    letter_2byte.add("노쇼")
    letter_2byte.add("노토")
    letter_2byte.add("노쿠")
    letter_2byte.add("네가")
    letter_2byte.add("니라")
    letter_2byte.add("다카")
    letter_2byte.add("도노")
    letter_2byte.add("만_")
    letter_2byte.add("모키")
    letter_2byte.add("무시")
    letter_2byte.add("미나")
    letter_2byte.add("미노")
    letter_2byte.add("미마")
    letter_2byte.add("미카")
    letter_2byte.add("라이")
    letter_2byte.add("라가")
    letter_2byte.add("로쿠")
    letter_2byte.add("료이")
    letter_2byte.add("바야")
    letter_2byte.add("보우")
    letter_2byte.add("부시")
    letter_2byte.add("비츠")
    letter_2byte.add("빗츄")
    letter_2byte.add("사키")
    letter_2byte.add("소노")
    letter_2byte.add("소우")
    letter_2byte.add("쇼지")
    letter_2byte.add("슈_")
    letter_2byte.add("스노")
    letter_2byte.add("세이")
    letter_2byte.add("센노")
    letter_2byte.add("시나")
    letter_2byte.add("시카")
    letter_2byte.add("시키")
    letter_2byte.add("아네")
    letter_2byte.add("아쿠")
    letter_2byte.add("야쿠")
    letter_2byte.add("안코")
    letter_2byte.add("야바")
    letter_2byte.add("야사")
    letter_2byte.add("야키")
    letter_2byte.add("우누")
    letter_2byte.add("우마")
    letter_2byte.add("우메")
    letter_2byte.add("우큐")
    letter_2byte.add("에몬")
    letter_2byte.add("에이")
    letter_2byte.add("에키")
    letter_2byte.add("엔랴")  # (延暦)寺
    letter_2byte.add("오시")
    letter_2byte.add("오우")
    letter_2byte.add("오이")
    letter_2byte.add("오치")
    letter_2byte.add("오케")
    letter_2byte.add("오헤")
    letter_2byte.add("요사")
    letter_2byte.add("이누")
    letter_2byte.add("이즈")
    letter_2byte.add("이쿠")
    letter_2byte.add("자와")
    letter_2byte.add("조우")
    letter_2byte.add("죠다")
    letter_2byte.add("지가")
    letter_2byte.add("츠키")
    letter_2byte.add("카마")
    letter_2byte.add("카케")
    letter_2byte.add("코노")
    letter_2byte.add("코코")
    letter_2byte.add("쿠보")
    letter_2byte.add("쿠지")  # 延(暦寺)
    letter_2byte.add("키시")
    letter_2byte.add("키쿠")
    letter_2byte.add("키츠")
    letter_2byte.add("타가")
    letter_2byte.add("타마")
    letter_2byte.add("테이")
    letter_2byte.add("테즈")
    letter_2byte.add("텐진")
    letter_2byte.add("토이")
    letter_2byte.add("토치")
    letter_2byte.add("톳토")
    letter_2byte.add("하마")
    letter_2byte.add("하쿠")
    letter_2byte.add("한냐")
    letter_2byte.add("효고")
    letter_2byte.add("후카")
    letter_2byte.add("후타")
    letter_2byte.add("히메")
    letter_2byte.add("하자")
    letter_2byte.add("한스")
    letter_2byte.add("후나")

    # Remove pairs that can be represented entirely with 1-byte fonts.
    letter_1byte = {letter.removeprefix("|") for letter in input_cand_1byte}

    def can_use_1byte(pair: str) -> bool:
        if len(pair) != 2:
            return False

        first, second = pair
        if first == "_":
            return second in letter_1byte
        if second == "_":
            return first in letter_1byte
        return first in letter_1byte and second in letter_1byte

    letter_2byte = {pair for pair in letter_2byte if not can_use_1byte(pair)}
    letter_2byte = list(letter_2byte)
    letter_2byte.sort()
    print(len(letter_2byte))

    start_code = "9540"  # 鼻
    input_cand = []
    input_cand.append(["은", font_name])
    input_cand.append(["는", font_name])
    input_cand.append(["이", font_name])
    input_cand.append(["가", font_name])
    input_cand.append(["을", font_name])
    input_cand.append(["를", font_name])
    input_cand.append(["와", font_name])
    input_cand.append(["과", font_name])
    input_cand.append(["에", font_name])
    input_cand.append(["의", font_name])
    code_dict, next_code = set_font(base_dir, font_table, src_font_canvas, start_code, 1, input_cand)
    ret_code_dict |= code_dict

    # set 4byte letters
    input_cand = []
    input_cand.append(["다이묘", font_name])
    input_cand.append(["와-과", font_name])
    input_cand.append(["은-는", font_name])
    input_cand.append(["을-를", font_name])
    input_cand.append(["이-가", font_name])

    input_cand.append(["나니와", font_name])
    input_cand.append(["도토미", font_name])
    input_cand.append(["마루네", font_name])
    input_cand.append(["무사시", font_name])
    input_cand.append(["미카와", font_name])
    input_cand.append(["사가미", font_name])
    input_cand.append(["사카이", font_name])
    input_cand.append(["스루가", font_name])
    input_cand.append(["시나노", font_name])
    input_cand.append(["아즈치", font_name])
    input_cand.append(["야마토", font_name])
    input_cand.append(["오사카", font_name])
    input_cand.append(["오와리", font_name])
    input_cand.append(["와시즈", font_name])
    input_cand.append(["와카사", font_name])
    input_cand.append(["에치고", font_name])
    input_cand.append(["에치젠", font_name])
    input_cand.append(["이나바", font_name])
    input_cand.append(["이와미", font_name])
    input_cand.append(["이즈모", font_name])
    input_cand.append(["치쿠젠", font_name])
    input_cand.append(["코즈케", font_name])
    input_cand.append(["키요스", font_name])
    input_cand.append(["타지마", font_name])
    input_cand.append(["하리마", font_name])

    code_dict, next_code = set_font(base_dir, font_table, src_font_canvas, next_code, 2, input_cand)
    ret_code_dict |= code_dict

    # set 6byte letters
    input_cand = []
    input_cand.append(["히에이산", font_name])

    code_dict, next_code = set_font(base_dir, font_table, src_font_canvas, next_code, 3, input_cand)
    ret_code_dict |= code_dict

    # Set merged 2byte letters
    letter_2byte = [[s, "default"] for s in letter_2byte]  # Change format
    ret_code_dict |= set_2byte_merge(base_dir, letter_2byte, font_table, src_font_canvas)

    # Save font canvas image
    dst_font_canvas_path = base_dir / f"taikou1-{font_file}"
    pil_img = Image.fromarray(src_font_canvas)
    one_bit_img = pil_img.convert("1")
    one_bit_img.save(dst_font_canvas_path)
    with open(base_dir / "custom_word.json", "w", encoding="utf-8") as f:
        json.dump(ret_code_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
