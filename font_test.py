from module.script import write_code


def main():
    bin_path = "C:/work_han/workspace2/Suikoden-DOS-KOR-dosbox/SUHOJI/MAIN.EXE"
    out_path = "C:/work_han/workspace2/Suikoden-DOS-KOR-dosbox/SUHOJI/MAIN.EXE"

    with open(bin_path, "rb") as f:
        data = f.read()
    data = bytearray(data)
    print(f"Data size: {bin_path}({len(data):,} bytes)")

    # write script
    addresses = [
        "33626=33635",
        "33811=33821",
    ]
    num_chars = [8, 8]
    code = 0xBDE0

    codes = []
    for num in num_chars:
        hex = f"{code:X}"
        codes.append(hex)
        code += num

    for code, num_char, address in zip(codes, num_chars, addresses):
        [start, end] = address.split("=")
        data = write_code(data, start, end, code, num_char)
        code_int = int(code, 16)
        for i in range(num_char):
            print(f"{code_int + i:X}=")

    # code = "8a"
    # for address in addresses:
    #     [start, end] = address.split("=")
    #     spos = int(start, 16)
    #     data[spos] = int(code, 16)
    #     data[spos + 1] = int(code, 16)
    #     data[spos + 2] = int("de", 16)
    #     data[spos + 3] = int(code, 16)
    #     data[spos + 4] = int("df", 16)

    # save data
    with open(out_path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
