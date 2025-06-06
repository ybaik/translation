import json
from pathlib import Path
from module.font_table import check_file, FontTable
from module.script import write_scripts
from module.check_script import check_script, diff_address
from rich.console import Console


def main():
    script_base_dir = Path("../workspace/m4")
    src_bin_base_dir = Path("../workspace/m4_jpn_all")
    dst_bin_base_dir = Path("../workspace/m4_kor")
    dst_font_table_path = "font_table/font_table-kor-jin.json"

    # ===================================================================
    # For debugging prints
    console = Console()

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
        src_data_path = src_bin_base_dir / str(
            file.relative_to(script_base_dir)
        ).replace("_kor.json", "")
        if not src_data_path.exists():
            print(f"{src_data_path.name} is not exists.")
            continue

        # Check dst data path
        dst_data_path = dst_bin_base_dir / src_data_path.relative_to(src_bin_base_dir)
        if dst_data_path.exists():
            continue

        if not dst_data_path.parent.exists():
            dst_data_path.parent.mkdir(parents=True, exist_ok=True)

        console.print(f"[yellow] Start:{src_data_path}[/yellow]")

        # Read scripts
        with open(src_script_path, "r", encoding="utf-8") as f:
            src_scripts = json.load(f)
        with open(dst_script_path, "r", encoding="utf-8") as f:
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
            console.print(
                f"[yellow] False length/letter count:{count_false_length},{count_false_letters}[/yellow]"
            )
            console.print(
                f"[yellow]The error should be fixed for[/yellow] [green]{src_data_path}[/green]"
            )
            return
        print(f"False length/letter count:{count_false_length},{count_false_letters}")
        console.print(f"[yellow] End:{src_data_path}[/yellow]")

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
