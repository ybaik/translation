import os
from module.font_table import check_file, FontTable
from module.script import write_scripts, write_code


def main():

    bin_path = "C:/dos/etc/macross2/S01_ARMY.BIN"
    font_path = "C:/work_han/workspace/anex86dos_m2.tbl"
    # read a font table
    if not check_file(font_path):
        return
    # font_table = FontTable(font_path)

    with open(bin_path, "rb") as f:
        data = f.read()
    data = bytearray(data)
    print(f"Data size: {bin_path}({len(data):,} bytes)")

    # write script
    scripts = {
        "69D=6B2": "께꼐꼬꼭꼴꾸꾹꾼꿀끄끅"
        # "69D=6B2": "어,아무도_없나?__"
    }

    # data = write_scripts(data, font_table, scripts)
    code = "927a"
    data = write_code(data, "69D", "6B2", code, 11)
    code_int = int(code, 16)
    for i in range(11):
        print(f"{code_int + i:x}=")

    # save data
    with open(bin_path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
