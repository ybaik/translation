import json
from pathlib import Path
from module.font_table import check_file, FontTable
from module.script import write_script, write_script_multibyte
from module.check_script import check_script, check_script_multibyte, diff_address
from rich.console import Console


def main():
    script_base_dir = Path("../workspace/script")
    src_bin_base_dir = Path("../workspace/rb1-PC98-JPN")
    dst_bin_base_dir = Path("../workspace/rb1-PC98-KOR")

    src_bin_base_dir = Path("../workspace/rb1-PC98-KOR_2nd")
    dst_bin_base_dir = Path("../workspace/rb1-PC98-KOR")

    dst_font_table_path = "font_table/font_table-kor-jin.json"
    dst_font_table_path = "../workspace/font_table-kor-rb1-1st.json"

    consider_multibyte = False
    # ===================================================================
    # For debugging prints
    console = Console()

    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_kor.json" in file.name:
            continue

        if "MAIN" not in file.name:
            continue

        # Check paths
        dst_script_path = file
        src_script_path = file.parent / file.name.replace("_kor.json", "_jpn.json")
        if not src_script_path.exists():
            print(f"{src_script_path.name} is not exists.")
            continue

        # Check a source data path
        src_data_path = src_bin_base_dir / str(
            file.relative_to(script_base_dir)
        ).replace("_kor.json", "")
        if not src_data_path.exists():
            print(f"{src_data_path.name} is not exists.")
            continue

        # Check a destination data path
        dst_data_path = dst_bin_base_dir / src_data_path.relative_to(src_bin_base_dir)
        # if dst_data_path.exists():
        #     continue

        if not dst_data_path.parent.exists():
            dst_data_path.parent.mkdir(parents=True, exist_ok=True)

        console.print(f"[yellow] Start:{src_data_path}[/yellow]")

        # Read source and destination script
        with open(src_script_path, "r", encoding="utf-8") as f:
            src_script = json.load(f)
        with open(dst_script_path, "r", encoding="utf-8") as f:
            dst_script = json.load(f)

        # Read a destinationfont table
        if not check_file(dst_font_table_path):
            return
        font_table = FontTable(dst_font_table_path)

        # Compare addresses in the source and destination scripts
        count_diff = diff_address(src_script, dst_script)
        if count_diff:
            return

        # Check the destination script
        if not consider_multibyte:
            count_false_length, count_false_letters = check_script(
                dst_script, font_table
            )
        else:
            count_false_length, count_false_letters = check_script_multibyte(
                dst_script, font_table
            )

        if count_false_length:
            console.print(
                f"[yellow] False length/letter count:{count_false_length},{count_false_letters}[/yellow]"
            )
        if count_false_letters:
            console.print(
                f"[yellow] False length/letter count:{count_false_length},{count_false_letters}[/yellow]"
            )
            return
        console.print(
            f"[yellow]The error should be fixed for[/yellow] [green]{src_data_path}[/green]"
        )

        print(f"False length/letter count:{count_false_length},{count_false_letters}")
        console.print(f"[yellow] End:{src_data_path}[/yellow]")

        # Read the source binary data
        if not check_file(src_data_path):
            return
        with open(src_data_path, "rb") as f:
            data = f.read()
        data = bytearray(data)
        console.print(f"Data size: {src_data_path}({len(data):,} bytes)")

        # Write the destination script to the binary data in memory
        if not consider_multibyte:
            data, valid_sentence_count = write_script(data, font_table, dst_script)
        else:
            data, valid_sentence_count = write_script_multibyte(
                data, font_table, dst_script
            )
        console.print(
            f"Valid sentence percentege: {valid_sentence_count/len(dst_script)*100:.2f}%"
        )

        # Save the replaced binary data to a file in the destination directory
        with open(dst_data_path, "wb") as f:
            f.write(data)


if __name__ == "__main__":
    main()
