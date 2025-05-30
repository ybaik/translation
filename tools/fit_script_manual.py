def main():
    script_range = [
        "B1D=B2E",
        "B39=B46",
        "B5F=B6C",
        "B85=B8C",
        "BA5=BB8",
        "BBC=BCB",
    ]
    script = "\
와…… 대단해……\
앗,꺄!   \
민메이씨!  \
아야!!\
큰일이네,라이트가 \
망가져버렸어. \
"
    script = script.replace(" ", "_")
    length = len(script)
    start = 0
    for line in script_range:
        codes = line.split("=")
        s_code_int = int(codes[0], 16)
        e_code_int = int(codes[1], 16)
        l_len = (e_code_int - s_code_int + 1) // 2

        if start + l_len <= length:
            print(l_len, script[start : start + l_len])
        else:
            print(l_len, script[start:])
        start += l_len

    print(length - start)


if __name__ == "__main__":
    main()
