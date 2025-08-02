import json
from typing import Dict, Tuple
from module.font_table import check_file, FontTable


def check_script(scripts: Dict, font_table: FontTable) -> Tuple[int, int]:
    """
    Check the script against the font table

    Parameters:
        scripts (Dict): The script to check.
        font_table (FontTable): The font table to check against.

    Returns:
        (int, int): A tuple containing the count of incorrect sentence lengths and incorrect characters.
    """
    # Check script
    count_false_length = 0
    count_false_characters = 0

    for address, sentence in scripts.items():
        if "=" not in address:
            continue
        length_from_address = font_table.check_length_from_address(address)
        length_from_sentence = font_table.check_length_from_sentence(sentence)
        if length_from_address != length_from_sentence:
            print(
                f"Wrong sentence length:{address}: {length_from_address}-{length_from_sentence}"
            )
            count_false_length += 1

        # Check if there is false characters in a sentence via comparison with the font table
        count_false_character, false_character = font_table.verify_sentence(sentence)
        if count_false_character:
            # print(f"Wrong letters:{address}: {count_false_character}-{false_character}")
            count_false_characters += count_false_character
            # Debug
            count_false_characters = 0

    return count_false_length, count_false_characters


def check_script_multibyte(scripts: Dict, font_table: FontTable) -> Tuple[int, int]:
    """
    Check the script against the font table

    Parameters:
        scripts (Dict): The script to check.
        font_table (FontTable): The font table to check against.

    Returns:
        (int, int): A tuple containing the count of incorrect sentence lengths and incorrect characters.
    """
    # Check script
    count_false_length = 0
    count_false_characters = 0

    for address, sentence in scripts.items():
        length_from_address = font_table.check_length_from_address(address)
        length_from_sentence = font_table.check_length_from_table(sentence)
        if length_from_address != length_from_sentence:
            print(
                f"Wrong sentence length:{address}: {length_from_address}-{length_from_sentence}"
            )
            count_false_length += 1

        # Check if there is false characters in a sentence via comparison with the font table
        count_false_character, false_character = font_table.verify_sentence(sentence)
        if count_false_character:
            print(f"Wrong letters:{address}: {count_false_character}-{false_character}")
            count_false_characters += count_false_character
            # Debug
            count_false_characters = 0

    return count_false_length, count_false_characters


def diff_address(src_script: Dict, dst_script: Dict) -> int:
    """
    Compare the address of two scripts

    Parameters:
        src_script (Dict): The script to check.
        dst_script (Dict): The script to check.

    Returns:
        int: The number of differences between the two scripts.
    """

    reversed = False
    if len(src_script.keys()) >= len(dst_script):
        scripts_1 = src_script
        scripts_2 = dst_script
    else:
        scripts_1 = dst_script
        scripts_2 = src_script
        reversed = True

    count_diff = 0
    for key, _ in scripts_1.items():
        if scripts_2.get(key) is None:
            if reversed:
                print(f"Diff = src address [], dst address [{key}]")
            else:
                print(f"Diff = src address [{key}], dst address []")
            count_diff += 1

    print(f"Number of diff = {count_diff}")
    return count_diff


def main():
    # read config
    config_path = "config.json"
    if not check_file(config_path):
        return
    with open("config.json") as f:
        config = json.load(f)

    # check source script
    src_script_path = config["src_script_file"]
    src_font_table_path = config["src_font_table_file"]
    if not check_file(src_script_path):
        return
    if not check_file(src_font_table_path):
        return

    print(f"check {src_script_path}...")
    with open(src_script_path, "r") as f:
        src_scripts = json.load(f)

    font_table = FontTable(src_font_table_path)
    count_false_length, count_false_letters = check_script(src_scripts, font_table)
    print(
        f"False sentence length and letter count: {count_false_length}, {count_false_letters}"
    )

    # check destination script
    dst_script_path = config["dst_script_file"]
    dst_font_table_path = config["dst_font_table_file"]
    if not check_file(dst_script_path):
        return
    if not check_file(dst_font_table_path):
        return

    print(f"check {dst_script_path}...")
    with open(dst_script_path, "r") as f:
        dst_scripts = json.load(f)

    font_table = FontTable(dst_font_table_path)
    count_false_length, count_false_letters = check_script(dst_scripts, font_table)
    print(
        f"False sentence length and letter count: {count_false_length}, {count_false_letters}"
    )

    diff_address(src_scripts, dst_scripts)


if __name__ == "__main__":
    main()
