import cv2
from PIL import Image
from module.font_table import FontTable
from module.font_image import return_img_roi


def crop_paste(img_src, img_dst, roi_src, roi_dst):
    img_dst[roi_dst[0] : roi_dst[1], roi_dst[2] : roi_dst[3]] = img_src[
        roi_src[0] : roi_src[1], roi_src[2] : roi_src[3]
    ]
    return img_dst


MOD_TABLE = {
    "824F": "간",
    "8250": "갈",
    "8251": "건",
    "8252": "게",
    "8253": "고",
    "8254": "곤",
    "8255": "그",
    "8256": "글",
    "8257": "길",
    "8258": "나",
    "8260": "네",
    "8261": "노",
    "8262": "니",
    "8263": "더",
    "8264": "도",
    "8265": "드",
    "8266": "들",
    "8267": "디",
    "8268": "라",
    "8269": "란",
    "826A": "랑",
    "826B": "래",
    "826C": "랜",
    "826D": "러",
    "826E": "레",
    "826F": "로",
    "8270": "론",
    "8271": "롤",
    "8272": "롬",
    "8273": "루",
    "8274": "룸",
    "8275": "르",
    "8276": "름",
    "8277": "리",
    "8278": "릭",
    "8279": "린",
    "8281": "링",
    "8282": "마",
    "8283": "맨",
    "8284": "머",
    "8285": "멜",
    "8286": "멧",
    "8287": "미",
    "8288": "밀",
    "8289": "바",
    "828A": "반",
    "828B": "버",
    "828C": "베",
    "828D": "볼",
    "828E": "브",
    "828F": "블",
    "8290": "비",
    "8291": "살",
    "8292": "샐",
    "8293": "선",
    "8294": "셀",
    "8295": "슐",
    "8296": "스",
    "8297": "슬",
    "8298": "시",
    "8299": "아",
    "829A": "안",
    "829F": "알",
    "82A0": "가",
    "82A1": "거",
    "8340": "에",
    "8341": "웰",
    "8342": "엘",
    "8343": "위",
    "8344": "오",
    "8345": "유",
    "8346": "올",
    "8347": "이",
    "8348": "왈",
    "8349": "인",
    "834A": "일",
    "834B": "딘",
    "834C": "임",
    "834D": "딩",
    "834E": "주",
    "834F": "랄",
    "8350": "즈",
    "8351": "록",
    "8352": "츠",
    "8353": "메",
    "8354": "치",
    "8355": "모",
    "8356": "카",
    "8357": "번",
    "8358": "캄",
    "8359": "사",
    "835A": "캔",
    "835B": "셰",
    "835C": "케",
    "835D": "슈",
    "835E": "켈",
    "835F": "온",
    "8360": "코",
    "8361": "와",
    "8362": "웨",
    "8363": "콜",
    "8364": "월",
    "8365": "크",
    "8366": "웬",
    "8367": "클",
    "8368": "잔",
    "8369": "키",
    "836A": "타",
    "836B": "탠",
    "836C": "터",
    "836D": "턴",
    "836E": "테",
    "836F": "제",
    "8370": "조",
    "8371": "텔",
    "8372": "즌",
    "8373": "지",
    "8374": "토",
    "8375": "칠",
    "8376": "칼",
    "8377": "톤",
    "8378": "퀸",
    "8379": "탈",
    "837A": "튜",
    "837B": "펜",
    "837C": "필",
    "837D": "트",
    "837E": "티",
    "8380": "파",
    "8381": "페",
    "8382": "포",
    "8383": "우",
    "8384": "퓌",
    "8385": "울",
    "8386": "프",
    "8387": "움",
    "8388": "플",
    "8389": "피",
    "838A": "하",
    "838B": "할",
    "838C": "해",
    "838D": "헬",
    "838F": "홀",
    "8390": "한",
    "8391": "휴",
    "8393": "히",
    "83C4": "앵",
    "83C5": "기",
    "83C6": "너",
    "83D4": "어",
    "83D5": "델",
    "83D6": "딕",
    "9540": "0",
    "9541": "1",
    "9542": "2",
    "9543": "3",
    "9544": "4",
    "9545": "5",
    "9546": "6",
    "9547": "7",
    "9548": "8",
    "9549": "9",
    "954A": "A",
    "954B": "B",
    "954C": "C",
    "954D": "D",
    "954E": "E",
    "954F": "F",
    "9550": "G",
    "9551": "H",
    "9552": "I",
    "9553": "J",
    "9554": "K",
    "9555": "L",
    "9556": "M",
    "9557": "N",
    "9558": "O",
    "9559": "P",
    "955A": "Q",
    "955B": "R",
    "955C": "S",
    "955D": "T",
    "955E": "U",
    "955F": "V",
    "9560": "W",
    "9561": "X",
    "9562": "Y",
    "9563": "Z",
    "9564": "a",
    "9565": "b",
    "9566": "c",
    "9567": "d",
    "9568": "e",
    "9569": "f",
    "956A": "g",
    "956B": "h",
    "956C": "i",
    "956D": "j",
    "956E": "k",
    "956F": "l",
    "9570": "m",
    "9571": "n",
    "9572": "o",
    "9573": "p",
    "9574": "q",
    "9575": "r",
    "9576": "s",
    "9577": "t",
    "9578": "u",
    "9579": "v",
    "957A": "w",
    "957B": "x",
    "957C": "y",
    "957D": "z",
}


def main():
    DEBUG = True
    src_font_bmp_path = "c:/work_han/font-kor-jin.bmp"
    dst_font_bmp_path = "c:/work_han/workspace/font-kor-rb1-BISCO.bmp"

    # Read font table
    src_font_table_path = "font_table/font_table-kor-jin.json"
    src_table = FontTable(src_font_table_path)

    # mod_font_table_path = "../workspace/font_table-kor-rb1-font-img-mod.json"
    # mod_table = FontTable(mod_font_table_path)

    img_src = cv2.imread(src_font_bmp_path, 0)
    img_dst = img_src.copy()

    if DEBUG:
        val_after = src_table.get_code("괌")
        val = src_table.get_code("가")
        print(val, val_after)
        roi = return_img_roi(val, DEBUG)
        # ypos = 33 * 16
        # xpos = 2 * 16
        # crop = img_src[ypos : ypos + 16, xpos : xpos + 16]
        crop = img_src[roi[0] : roi[1], roi[2] : roi[3]]
        crop_resized = cv2.resize(crop, dsize=(128, 128), interpolation=cv2.INTER_AREA)
        cv2.imshow("patch_empty", crop_resized)
        cv2.waitKey(1000)
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
