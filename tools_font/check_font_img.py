import cv2
import numpy as np
from module.font_image import return_img_roi


def crop_paste(img_src, img_dst, roi_src, roi_dst):
    img_dst[roi_dst[0] : roi_dst[1], roi_dst[2] : roi_dst[3]] = img_src[
        roi_src[0] : roi_src[1], roi_src[2] : roi_src[3]
    ]
    return img_dst


def main():
    font_bmp_path = "c:/work_han/workspace4/inindo-font-kor.bmp"
    img_src = cv2.imread(font_bmp_path, 0)

    code = "97B397B4"
    code = code.replace("0x:", "")
    code = code.split("#")[0]

    if len(code) % 2 != 0:
        assert 0, f"The length of code is not matched. {code}"

    num_chars = len(code) // 4
    canvas = np.zeros((16, num_chars * 16), dtype=np.uint8)
    for i in range(num_chars):
        roi = return_img_roi(code[i * 4 : (i + 1) * 4])
        # ypos = 33 * 16
        # xpos = 2 * 16
        # crop = img_src[ypos : ypos + 16, xpos : xpos + 16]

        canvas[:, 16 * i : 16 * (i + 1)] = img_src[roi[0] : roi[1], roi[2] : roi[3]]

    h, w = canvas.shape
    nh = h * 8
    nw = w * 8
    resized = cv2.resize(canvas, dsize=(nw, nh), interpolation=cv2.INTER_AREA)
    cv2.imshow("patch", resized)
    cv2.waitKey(1000)
    cv2.imwrite("debug.jpg", resized)


if __name__ == "__main__":
    main()
