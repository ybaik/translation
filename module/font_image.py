import cv2
import numpy as np

from typing import List, Dict, Tuple


# Font image info
# Entire font image size = 2048x2048
# Font patch size = 16x16
# Font patch array size = 128x128


def return_img_roi(code_hex: str, debug=False) -> Tuple[int, int, int, int]:
    """
    Return the pixel ROI (row pixel start, row pixel end, column pixel start, column pixel end) based on the input font code

    Args:
    code_hex (str): A hexadecimal code as a string, e.g., "8140".

    Returns:
    Tuple[int, int, int, int]: Y start, Y end, X start, X end.
    """
    code = int(code_hex, 16)

    code_prefix = (code >> 8) & 0xFF
    code_suffix = code & 0xFF

    if debug:
        print(f"{code_prefix:X} {code_suffix:X}")

    # Set column (X)
    col = (code_prefix - 0x81) * 2 + 1
    col += 1 if code_suffix >= 0x9F else 0

    # Set row (Y)
    if code_suffix >= 0x9F:
        row = 33 + code_suffix - 0x9F
    else:
        row = 33 + code_suffix - 0x40
        if code_suffix >= 0x80:
            row -= 1

    # Set a patch ROI
    if debug:
        print(row, col)
    ypos = row * 16
    xpos = col * 16
    return [ypos, ypos + 16, xpos, xpos + 16]


def return_img_roi_1byte(code_hex: str, debug=False) -> Tuple[int, int, int, int]:
    """
    Return the pixel ROI (row pixel start, row pixel end, column pixel start, column pixel end) based on the input font code

    Args:
    code_hex (str): A hexadecimal code as a string, e.g., "8140".

    Returns:
    Tuple[int, int, int, int]: Y start, Y end, X start, X end.
    """
    code = int(code_hex, 16)
    if code > 0xFF or code < 0:
        raise ValueError(f"{code_hex} is not a supported range.")

    col = code
    row = 0

    # Set a patch ROI
    if debug:
        print(row, col)
    ypos = row * 16
    xpos = col * 8
    return [ypos, ypos + 16, xpos, xpos + 8]


def imread_korean(path):
    img_array = np.fromfile(path, np.uint8)
    img = cv2.imdecode(img_array, 0)
    return img


def crop_paste(img_src, img_dst, roi_src, roi_dst):
    img_dst[roi_dst[0] : roi_dst[1], roi_dst[2] : roi_dst[3]] = img_src[
        roi_src[0] : roi_src[1], roi_src[2] : roi_src[3]
    ]
    return img_dst


def draw_letters_on_canvas(
    font_canvas: np.ndarray,
    input_cands: List,
    img_path_dict: Dict,
    code_list: List[str],
    num_letters: int,
    need_merge=False,
) -> Dict[str, str]:
    code_idx = 0
    ret_dict_code = dict()

    # Update font canvas
    for korean, font_name in input_cands:
        if not need_merge:
            if korean not in img_path_dict[font_name]:
                code_idx += num_letters
                continue
            word_img = imread_korean(str(img_path_dict[font_name][korean]))
            code_tag = ""
            for i in range(num_letters):
                code = code_list[code_idx + i]
                roi = return_img_roi(code)
                font_canvas[roi[0] : roi[1], roi[2] : roi[3]] = word_img[0:16, 16 * i : 16 * i + 16]
                code_tag += code
            ret_dict_code[korean] = code_tag
            code_idx += num_letters
        else:  # Need to merge
            word_img = np.full((16, 16), 255, dtype=np.uint8)

            word_img[:, 0:8] = imread_korean(str(img_path_dict[font_name][korean[0]]))
            if korean[1] != "_":
                word_img[:, 8:] = imread_korean(str(img_path_dict[font_name][korean[1]]))

            code = code_list[code_idx]
            roi = return_img_roi(code)
            font_canvas[roi[0] : roi[1], roi[2] : roi[3]] = word_img
            code_idx += 1
            ret_dict_code[korean] = code

    return ret_dict_code
