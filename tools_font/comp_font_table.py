import json
from pathlib import Path
from module.font_table import FontTable

def find_code(char, tbl):
    for code in tbl.keys():
        if tbl[code] == char:
            return code
    return None


def main():
    base_path = Path("c:/work_han")
    src_path = base_path / "anex86dos_m3.tbl"
    dst_path = base_path / "anex86dos_m2.tbl"

    ft_src = FontTable(src_path)
    ft_dst = FontTable(dst_path)

    count = 0
    for k, v in ft_dst.code2char.items():
        c = ft_dst.get_char(k)
        if c != v:
            print(k, v, c)
            count +=1

    print(count)

    print(1)
    # with open(src_path, "r") as f:
    #     src_tbl = json.load(f)
    # with open(dst_path, "r") as f:
    #     dst_tbl = json.load(f)

    # print(len(src_tbl.keys()), len(dst_tbl.keys()))


    # print(find_code("권", dst_tbl))
    # print(find_code("곁", dst_tbl))
    # print(find_code("횔", dst_tbl))
    # print(find_code("힝", dst_tbl))

    return

    for code in src_tbl.keys():
        src_char = src_tbl.get(code)
        dst_char = dst_tbl.get(code)
        if src_char != dst_char:
            print(code, src_char, dst_char)
            continue


if __name__ == '__main__':
    main()
