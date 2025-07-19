import cv2
from PIL import Image
from module.font_table import FontTable
from module.font_image import *


def crop_paste(img_src, img_dst, roi_src, roi_dst):
    img_dst[roi_dst[0] : roi_dst[1], roi_dst[2] : roi_dst[3]] = img_src[
        roi_src[0] : roi_src[1], roi_src[2] : roi_src[3]
    ]
    return img_dst


def main():
    DEBUG = True
    src_font_bmp_path = "c:/work_han/workspace/BISCO.bmp"
    dst_font_bmp_path = "c:/work_han/workspace/font-kor-rb1-BISCO.bmp"

    # Read font table
    src_font_table_path = "font_table/font_table-kor-jin.json"
    src_table = FontTable(src_font_table_path)

    mod_font_table_path = "../workspace/font_table-kor-rb1-font-img-mod.json"
    mod_table = FontTable(mod_font_table_path)

    img_src = cv2.imread(src_font_bmp_path, 0)
    img_dst = img_src.copy()

    if DEBUG:
        val = "0x45"
        print(val)
        roi = return_img_roi_1byte(val, DEBUG)
        # ypos = 0 * 16
        # xpos = 48 * 8
        # crop = img_src[ypos : ypos + 16, xpos : xpos + 8]
        crop = img_src[roi[0] : roi[1], roi[2] : roi[3]]
        crop_resized = cv2.resize(crop, dsize=(64, 128), interpolation=cv2.INTER_AREA)
        cv2.imshow("patch_empty", crop_resized)
        cv2.waitKey()
        return
    else:
        # for dst_code, src_char in mod_table.code2char.items():
        for dst_code, src_char in MOD_TABLE.items():
            src_code = src_table.get_code(src_char)
            src_roi = return_img_roi(src_code)
            dst_roi = return_img_roi(dst_code)
            if src_roi == dst_roi:
                continue
            print(src_char)
            img_dst = crop_paste(img_src, img_dst, src_roi, dst_roi)

    # Thresholding
    img_pil = Image.fromarray(img_dst).convert("1")
    img_pil.save(dst_font_bmp_path)


if __name__ == "__main__":
    main()
