import json
from pathlib import Path


# Dialog dictionary
def main():
    base_dir = Path("c:/work_han/workspace")
    script_base_dir = base_dir / "m2"
    data_base_dir = base_dir / "m2_kor"
    data_base_dir = base_dir / "Macross2_jpn"

    find_source = True

    sentence = "エキセドル"
    sentence_kor = "기록참모 엑세돌 "
    sentence_kor = sentence_kor.replace(" ", "_")

    count = 0

    # read a pair of scripts
    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_jpn.json" in file.name:
            continue
        dst_path = file.parent / file.name.replace("_jpn.json", "_kor.json")
        if not dst_path.exists():
            continue

        need_update = False
        with open(file, "r") as f:
            src = json.load(f)
        with open(dst_path, "r") as f:
            dst = json.load(f)

        # check address
        buf_address = ""
        buf_src_sentence = ""
        buf_dst_sentence = ""

        if not find_source:
            for address, dst_sentence in dst.items():
                if sentence_kor not in dst_sentence:
                    buf_address = address
                    buf_dst_sentence = dst_sentence
                    buf_src_sentence = src[address]
                    continue

                print("=============================")
                print(buf_address)
                print(buf_src_sentence)
                print(buf_dst_sentence)
                print(file.name, address)
                print(src[address])
                print(dst_sentence)
                print("=============================")
        else:

            data_path = data_base_dir / file.name.replace("_jpn.json", "")
            with open(data_path, "rb") as f:
                data = f.read()
                data = bytearray(data)

            candidates = [
                "ミリア",
                "エキセドル",
                "ブリタイ",
                "デワントン",
                "カムジン",
                "コンダ",
                "ワレラ",
                "ロリ-",
            ]

            addresses = []
            new_addresses = []
            new_sentences = []

            for address, src_sentence in src.items():
                # if sentence not in src_sentence:
                #     continue
                # stop = False
                # for candidate in candidates:
                #     if candidate in src_sentence:
                #         stop = True
                #         break
                # if stop:
                #     continue

                [code_hex_start, code_hex_end] = address.split("=")
                spos = int(code_hex_start, 16)
                epos = int(code_hex_end, 16)

                if len(src_sentence) * 2 != epos - spos + 1:
                    continue

                if epos < len(data) + 6:
                    ccc = data[epos + 1 : epos + 3]
                    if int("39", 16) >= ccc[0] >= int("30", 16) and int(
                        "39", 16
                    ) >= ccc[1] >= int("30", 16):
                        string = ""
                        for i in range(5):
                            val = int(data[epos + i + 1]) - 48
                            if 9 >= val >= 0:
                                string += f"|{val}"

                        if len(string) > 0:
                            additional_byte = len(string) // 2
                            new_address = f"{spos:05X}={epos+additional_byte:05X}"
                            new_sentence = src_sentence + string

                            addresses.append(address)
                            new_addresses.append(new_address)
                            new_sentences.append(new_sentence)
                            count += 1

                            print("=============================")
                            print(file.name, address)
                            print(src_sentence + string)
                            # print(dst[address])
                            print("=============================")

            if len(addresses) > 0:
                for i in range(len(addresses)):
                    src[new_addresses[i]] = src.pop(
                        addresses[i]
                    )  # To preserve the original order
                    src[new_addresses[i]] = new_sentences[i]
                need_update = True

            if need_update:
                sorted_src = {k: src[k] for k in sorted(src)}
                with open(file, "w") as f:
                    json.dump(sorted_src, f, ensure_ascii=False, indent=4)
                print(1)

    print(count)


if __name__ == "__main__":
    main()
