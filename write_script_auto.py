import json
from pathlib import Path
from module.font_table import check_file, FontTable
from module.script import write_scripts
from check_script import check_script, diff_address
from rich.console import Console


def main():
    script_base_dir = Path("../workspace/m3")
    src_bin_base_dir = Path("../workspace/Macross3_jpn")
    dst_bin_base_dir = Path("../workspace/m3_kor")
    dst_font_table_path = "font_table/font_table-kor-jin.json"

    # ===================================================================

    for file in script_base_dir.rglob("*.json"):  # Use rglob to search subdirectories
        if not "_kor.json" in file.name:
            continue

        # Check paths
        dst_script_path = file
        src_script_path = file.parent / file.name.replace("_kor.json", "_jpn.json")
        if not src_script_path.exists():
            print(f"{src_script_path.name} is not exists.")
            continue

        # Check src data path
        src_data_path = src_bin_base_dir / file.name.replace("_kor.json", "")
        if not src_data_path.exists():
            print(f"{src_data_path.name} is not exists.")
            continue

        # Check src data path
        dst_data_path = dst_bin_base_dir / src_data_path.name

        # Read scripts
        with open(src_script_path, "r") as f:
            src_scripts = json.load(f)
        with open(dst_script_path, "r") as f:
            dst_scripts = json.load(f)

        # read a font table
        if not check_file(dst_font_table_path):
            return
        font_table = FontTable(dst_font_table_path)

        # check address
        count_diff = diff_address(src_scripts, dst_scripts)
        if count_diff:
            return

        # check scripts
        count_false_length, count_false_letters = check_script(dst_scripts, font_table)

        if count_false_length or count_false_letters:
            console = Console()
            console.print(
                f"[yellow] False length/letter count:{count_false_length},{count_false_letters}[/yellow]"
            )
            console.print(
                f"[yellow]The error should be fixed for[/yellow] [green]{src_data_path}[/green]"
            )
            return
        print(f"False length/letter count:{count_false_length},{count_false_letters}")

        # read the target (jpn) data
        if not check_file(src_data_path):
            return
        with open(src_data_path, "rb") as f:
            data = f.read()
        data = bytearray(data)
        print(f"Data size: {src_data_path}({len(data):,} bytes)")

        # write scripts
        data = write_scripts(data, font_table, dst_scripts)

        # save data
        with open(dst_data_path, "wb") as f:
            f.write(data)


if __name__ == "__main__":
    main()
