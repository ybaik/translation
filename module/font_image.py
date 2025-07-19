from typing import Tuple


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
        assert 0, f"{code_hex} is not a supproted range."

    col = code
    row = 0
    

    # Set a patch ROI
    if debug:
        print(row, col)
    ypos = row * 16
    xpos = col * 8
    return [ypos, ypos + 16, xpos, xpos + 8]