from pathlib import Path
from rich.console import Console

from module.script import Script
from module.font_table import FontTable
from module.check_script import diff_address


def main():
    # platform = "dos"
    platform = "pc98"

    script_base_dir = Path(f"../workspace3/script-{platform}")
    src_bin_base_dir = Path(f"../workspace3/jpn-{platform}")
    dst_bin_base_dir = Path(f"../workspace3/kor-{platform}")

    # src_bin_base_dir = Path("../workspace/rb1-PC98-KOR-backup")
    # dst_bin_base_dir = Path("../workspace/rb1-PC98-KOR")

    src_font_table_path = "font_table/font_table-jpn-full.json"
    dst_font_table_path = "font_table/font_table-kor-jin.json"
    # dst_font_table_path = "../workspace/font_table-kor-rb1-1st.json"

    # ===================================================================
    # For debugging prints
    console = Console()

    for file in script_base_dir.glob("*.json"):  # Use rglob to search subdirectories
        if "_kor.json" not in file.name:
            continue

        if "MAIN.EXE" not in file.name:
            continue

        # Check paths
        dst_script_path = file
        src_script_path = file.parent / file.name.replace("_kor.json", "_jpn.json")
        if not src_script_path.exists():
            print(f"{src_script_path.name} is not exists.")
            continue

        # Check a source data path
        src_data_path = src_bin_base_dir / str(file.relative_to(script_base_dir)).replace("_kor.json", "")
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

        # Read source and destination font tables
        src_font_table = FontTable(src_font_table_path)
        dst_font_table = FontTable(dst_font_table_path)

        # Read source and destination script
        src_script = Script(str(src_script_path))
        dst_script = Script(str(dst_script_path))

        # Compare addresses in the source and destination scripts
        count_diff = diff_address(src_script.script, dst_script.script)
        if count_diff:
            return

        # Check the destination script
        count_false_length, count_false_letters = dst_script.validate(dst_font_table)

        if count_false_length:
            console.print(f"[yellow] False length/letter count:{count_false_length},{count_false_letters}[/yellow]")
        if count_false_letters:
            console.print(f"[yellow] False length/letter count:{count_false_length},{count_false_letters}[/yellow]")
            return

        print(f"False length/letter count:{count_false_length},{count_false_letters}")
        console.print(f"[yellow] End:{src_data_path}[/yellow]")

        # Check source script with binary data
        is_diff = src_script.validate_with_binary(src_font_table, src_data_path)
        if is_diff:
            console.print(f"[yellow] json and data doesn't match.[/yellow] [green]{src_data_path}[/green]")

        # Read the source binary data
        if not Path(src_data_path).exists():
            return
        with open(src_data_path, "rb") as f:
            data = f.read()
        data = bytearray(data)
        console.print(f"Data size: {src_data_path}({len(data):,} bytes)")

        # Write the destination script to the binary data in memory
        data, valid_sentence_count = dst_script.write_script(data, dst_font_table)
        if len(dst_script.script):
            valid_p = valid_sentence_count / len(dst_script.script) * 100
            msg = f"Valid sentence percentege (done/total): {valid_p:.2f}%"
            msg += f" ({valid_sentence_count}/{len(dst_script.script)})"
            console.print(msg)

        # Save the replaced binary data to a file in the destination directory
        with open(dst_data_path, "wb") as f:
            f.write(data)


if __name__ == "__main__":
    main()
