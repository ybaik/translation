import json
import copy
from pathlib import Path
from typing import Dict, Tuple
from module.font_table import FontTable


def check_script(scripts: Dict, font_table: FontTable, custom_words: Dict = None) -> Tuple[int, int]:
    """
    Check the script against the font table

    Parameters:
        scripts (Dict): The script to check.
        font_table (FontTable): The font table to check against.
        custom_words (Dict): A dictionary of custom words and their hex values.

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
        length_from_sentence = font_table.check_length_from_sentence(sentence, custom_words)
        if length_from_address != length_from_sentence:
            print(f"Wrong sentence length:{address}: {length_from_address}-{length_from_sentence}")
            count_false_length += 1

        # Check if there is false characters in a sentence via comparison with the font table
        count_false_character, false_character = font_table.verify_sentence(sentence)
        if count_false_character:
            # print(f"Wrong letters:{address}: {count_false_character}-{false_character}")
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
        scripts_1 = copy.deepcopy(src_script)
        scripts_2 = copy.deepcopy(dst_script)
    else:
        scripts_1 = copy.deepcopy(dst_script)
        scripts_2 = copy.deepcopy(src_script)
        reversed = True

    # Remove custom input
    scripts_1.pop("custom_input", None)
    scripts_2.pop("custom_input", None)

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
    with open("config.json") as f:
        config = json.load(f)

    # check source script
    src_script_path = Path(config["src_script_file"])
    src_font_table_path = Path(config["src_font_table_file"])

    print(f"check {src_script_path}...")
    with open(src_script_path, "r", encoding="utf-8") as f:
        src_scripts = json.load(f)

    src_custom_word_path = src_script_path.parent / "custom_word.json"
    src_custom_words = {}
    if src_custom_word_path.exists():
        with open(src_custom_word_path, "r", encoding="utf-8") as f_custom:
            src_custom_words = json.load(f_custom)

    font_table = FontTable(src_font_table_path)
    count_false_length, count_false_letters = check_script(src_scripts, font_table, src_custom_words)
    print(f"False sentence length and letter count: {count_false_length}, {count_false_letters}")

    # check destination script
    dst_script_path = Path(config["dst_script_file"])
    dst_font_table_path = Path(config["dst_font_table_file"])

    print(f"check {dst_script_path}...")
    with open(dst_script_path, "r", encoding="utf-8") as f:
        dst_scripts = json.load(f)

    dst_custom_word_path = dst_script_path.parent / "custom_word.json"
    dst_custom_words = {}
    if dst_custom_word_path.exists():
        with open(dst_custom_word_path, "r", encoding="utf-8") as f_custom:
            dst_custom_words = json.load(f_custom)

    font_table = FontTable(dst_font_table_path)
    count_false_length, count_false_letters = check_script(dst_scripts, font_table, dst_custom_words)
    print(f"False sentence length and letter count: {count_false_length}, {count_false_letters}")

    diff_address(src_scripts, dst_scripts)


if __name__ == "__main__":
    main()
