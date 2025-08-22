from module.script import Script
from module.font_table import FontTable


def main():
    platform = "pc98"
    target_file = "MAIN.EXE"
    locale = "kor"
    script_path = f"C:/work_han/workspace0/script-{platform}/{target_file}_{locale}.json"
    binary_path = f"C:/work_han/workspace0/{locale}-{platform}/{target_file}"
    font_table_path = "font_table/font_table-jpn-full.json"
    # font_table_path = "font_table/font_table-jpn-full.json"

    dst_script_path = f"C:/work_han/workspace0/script-{platform}/{target_file}_{locale}.json"

    font_table = FontTable(font_table_path)
    script = Script(script_path)

    count_false_length, count_false_caracters = script.validate(font_table)
    print(f"False length/letter count:{count_false_length},{count_false_caracters}")

    # code
    control_codes = {
        "0A": "␂",
        "1B": "␊",
    }
    split_code = "␂"

    is_connected = False
    is_merged = False
    is_split = False
    is_connected = script.attach_control_codes(binary_path, control_codes)
    is_merged = script.merge_sentences()
    # is_split = script.split_sentences(font_table, split_code)

    # Save the modified script
    if is_connected or is_merged or is_split:
        if is_connected:
            print("The sentences are connected.")
        if is_merged:
            print("The sentences are merged.")
        if is_split:
            print("The sentences are split.")
        script.save(dst_script_path)

    # script.set_custom_codes(control_codes)
    # script.save(dst_script_path)

    # is_filtered = script.filter_sentences()
    # if is_filtered:
    #     print("The sentences are filtered.")
    #     script.save(dst_script_path)


if __name__ == "__main__":
    main()
