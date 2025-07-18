import os
from module.font_table import check_file, FontTable
from module.script import write_code, write_code_1byte


def main():

    bin_path = "C:/work_han/workspace/rb1-PC98-JPN/MAIN.EXE"
    out_path = "C:/work_han/workspace/MAIN.EXE"

    font_path = "C:/work_han/workspace/anex86dos_m2.tbl"
    # read a font table
    # if not check_file(font_path):
    #     return
    # font_table = FontTable(font_path)

    with open(bin_path, "rb") as f:
        data = f.read()
    data = bytearray(data)
    print(f"Data size: {bin_path}({len(data):,} bytes)")

    # write script
    scripts = {"69D=6B2": "께"}

    # data = write_scripts(data, font_table, scripts)
    addresses = [
        "287B7=287BC",
    ]

    # codes = ["8e"]
    # num_chars = 1
    # for code, address in zip(codes, addresses):
    #     [start, end] = address.split("=")
    #     data = write_code_1byte(data, start, end, code, num_chars)
    #     code_int = int(code, 16)
    #     for i in range(num_chars):
    #         print(f"{code_int + i:X}=")

    code = "8a"
    for address in addresses:
        [start, end] = address.split("=")
        spos = int(start, 16)
        data[spos] = int(code, 16)
        data[spos + 1] = int(code, 16)
        data[spos + 2] = int("de", 16)
        data[spos + 3] = int(code, 16)
        data[spos + 4] = int("df", 16)

    # save data
    with open(out_path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
