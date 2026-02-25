from pathlib import Path
from module.script import Script
from module.font_table import FontTable


def main():
    platform = "dos"
    platform = "pc98"
    ws_num = 4
    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    script_base_dir = base_dir / f"script-{platform}"
    dst_script_base_dir = base_dir / f"script-{platform}-steam"
    dst_bin_base_dir = base_dir / f"jpn-{platform}-steam"
    src_font_table_path = Path("font_table/font_table-jpn-full.json")

    src_jpn_script_path = script_base_dir / "MAIN.EXE_jpn.json"
    src_kor_script_path = script_base_dir / "MAIN.EXE_kor.json"
    dst_bin_path = dst_bin_base_dir / "MAIN.EXE"
    dst_jpn_script_path = dst_script_base_dir / src_jpn_script_path.name
    dst_kor_script_path = dst_script_base_dir / src_kor_script_path.name

    src_jpn_script = Script(str(src_jpn_script_path))
    src_kor_script = Script(str(src_kor_script_path))
    dst_jpn_script = Script()
    dst_kor_script = Script()

    dst_bin = bytearray(open(dst_bin_path, "rb").read())
    src_font_table = FontTable(src_font_table_path, script_base_dir)

    pos = 0
    for address, sentence_jpn in src_jpn_script.script.items():
        start, end = address.split("=")
        start = int(start, 16)
        end = int(end, 16)
        length = end - start + 1

        if "0x:" in sentence_jpn:
            combined_hex = sentence_jpn.replace("0x:", "")
        else:
            # Extract bytes from source string
            hex_strings = src_font_table.get_codes(sentence_jpn)
            combined_hex = "".join(hex_strings)
        result_bytes = bytearray.fromhex(combined_hex)

        # Find matches
        position = dst_bin[pos:].find(result_bytes)
        position = position + pos
        if position == -1:
            print(f"Can't find match: {address}:{sentence_jpn}")
            continue
            # return

        start_new = position
        end_new = position + length - 1
        address_new = f"{start_new:05X}={end_new:05X}"
        dst_jpn_script.script[address_new] = sentence_jpn
        dst_kor_script.script[address_new] = src_kor_script.script[address]

        pos = end_new + 1

    dst_jpn_script.save(dst_jpn_script_path)
    dst_kor_script.save(dst_kor_script_path)


if __name__ == "__main__":
    main()
