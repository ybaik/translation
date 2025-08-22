import numpy as np
import cv2
from module.font_table import FontTable


def mse(img1, img2):
    h, w = img1.shape
    err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    err /= float(h * w)
    return err


def match_patch(patch, img):
    cnt = 0
    min_cnt = -1
    min_error = 10000
    for x in range(16, 41):
        for y in range(33, 127):
            ypos = y * 16
            xpos = x * 16
            crop = img[ypos : ypos + 16, xpos : xpos + 16]
            error = mse(crop, patch)
            if min_error > error:
                min_error = error
                min_cnt = cnt
            if error == 0:
                return cnt, error
            cnt += 1
    return min_cnt, min_error


def main():
    # json_font_table_path = "font_table/font_table-kor-jin.json"
    json_font_table_path = "font_table/font_table-kor-jin.json"
    font_bmp_path = "D:/work_han/font-kor-jin.bmp"
    font_table = FontTable(json_font_table_path)
    font_table2 = FontTable("D:/work_han/workspace/font_table-jpn-full.json")
    font_bmp_path1 = "D:/work_han/font-kor-jin.bmp"
    font_bmp_path1 = "D:/work_han/workspace/anex86_bajin.bmp"
    font_bmp_path2 = "D:/work_han/workspace/anex86_ba.bmp"

    chars = list(font_table.char2code.keys())
    # codes = list(font_table.code2char.keys())
    chars = chars[len(chars) - 2350 :]
    # codes = codes[len(codes)-2350:]

    codes = list(font_table2.code2char.keys())

    print(len(chars))

    img1 = cv2.imread(font_bmp_path1, 0)
    img2 = cv2.imread(font_bmp_path2, 0)

    ypos = 33 * 16
    xpos = 15 * 16
    patch_empty = img1[ypos : ypos + 16, xpos : xpos + 16]

    cnt = 0
    code2char = dict()
    # for x in range(16, 41):
    for x in range(41, 48):
        for y in range(33, 127):
            print(x, y)
            ypos = y * 16
            xpos = x * 16
            crop2 = img2[ypos : ypos + 16, xpos : xpos + 16]

            if x == 26 and y == 108:
                cnt += 1
                continue  # 뵈
            if x == 26 and y == 109:
                cnt += 1
                continue  # 뵉
            if x == 37 and y == 93:
                cnt += 1
                continue  # 큩

            if x == 41 and y == 44:
                cnt += 1
                continue  # 훱
            if x == 42 and y == 81:
                cnt += 1
                continue  # 츝
            if x == 47 and y == 79:
                cnt += 1
                continue  # 흗

            error = mse(crop2, patch_empty)
            if error == 0:
                cnt += 1
                continue

            # found character
            val, min_err = match_patch(crop2, img1)
            if min_err != 0:
                k = list(code2char.keys())[-1]
                v = code2char[k]
                print(x, y, k, v, min_err)
                vis = cv2.resize(crop2, dsize=(128, 128), interpolation=cv2.INTER_AREA)
                cv2.imshow("test", vis)
                cv2.waitKey()
            # print(codes[cnt], chars[val])
            code2char[codes[cnt]] = chars[val]
            cnt += 1

    table_for_tbl = ""
    for code, letter in sorted(code2char.items()):
        table_for_tbl += f"{code}={letter}\n"
    file_path = "D:/work_han/workspace/new.tbl"
    with open(file_path, "w") as f:
        f.write(table_for_tbl)

    return

    # r94-c17

    # KS X 1001 기준 - 2350

    # 2048 x 2048 x 1
    # (128x128) x (16x16)
    # img = cv2.imread(font_bmp_path, 0)

    # 16 33
    # s = int('9f', 16)
    # e = int('fc', 16)+1

    # s = int('40', 16)
    # e = int('9e', 16)+1

    # cnt = 0
    # for v in range(s, e):
    #     code_hex = f"89{v:2x}"
    #     char = font_table.get_char(code_hex)
    #     if char is not None:
    #         cnt += 1
    #     else:
    #         print(code_hex)

    # print(cnt)

    # x = 16*16
    # y = 33*16

    # crop = img[y:y+16, x:x+16]
    # crop_resized = cv2.resize(crop, dsize=(128, 128), interpolation=cv2.INTER_AREA)

    # cv2.imshow("a", crop_resized)
    # cv2.waitKey()


if __name__ == "__main__":
    main()
