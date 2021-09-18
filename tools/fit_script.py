import os
import json

def main():
    script_range = [
    "0x19fd=0x1a1e",
    "0x1a38=0x1a4b",
    "0x1a6b=0x1a92",
    "0x1aac=0x1ad1",
    "0x1aeb=0x1b04",
    "0x1b1e=0x1b39",
    "0x1b53=0x1b72",
    "0x1b8c=0x1bab",
    "0x1bc5=0x1be6",
    ]

    script = "\
기획/시나리오_야마시타_카츠히로\
프로그램__나카모리\
사운드__TOYO_KUSANAGI__\
그래픽_수석__야미츠다_마키코___\
그래픽_ 요코야마 리  \
그래픽__스기모토_미노루시\
특별 감사 _이카라시_칸   \
특별 감사 _후쿠하라_카즈히코\
특별 감사  신도_에미코    \
"
    script = script.replace(' ', '_')
    length = len(script)
    start = 0
    for line in script_range:
        codes = line.split('=')
        s_code_int = int(codes[0], 16)
        e_code_int = int(codes[1], 16)
        l_len = (e_code_int - s_code_int + 1)//2

        if start + l_len <= length:
            print(l_len, script[start:start+l_len])
        else:
            print(l_len, script[start:])
        start += l_len

    print(length - start)





if __name__ == "__main__":
    main()