import json

from font_table import check_file, read_font_table

def check_script(scripts, font_table):

    # value-table
    letters = list(set(font_table.values()))

    # check script
    iteration = scripts.keys()
  
    count_false_length = 0
    count_false_letters = 0
    for range, sentence in scripts.items():
        # check sentence length
        [code_hex_start, code_hex_end] = range.split('=')
        address_length = (int(code_hex_end, 16) - int(code_hex_start, 16)+1)//2
        sentence_length =len(sentence)
        if address_length != sentence_length:
            print(f'Wrong sentence length:{range}: {address_length}-{sentence_length}')
            count_false_length += 1

        # check false letters        
        count_false_char = 0
        false_char = ''
        for character in sentence:
            if character not in letters:
                count_false_char += 1
                false_char += character
        if count_false_char:
            print(f'Wrong letters:{range}: {count_false_char}-{false_char}')
            count_false_letters += count_false_char

    return count_false_length, count_false_letters


def main():
    # read config
    config_path = 'config.json'
    if not check_file(config_path): return
    with open('config.json') as f:
        config = json.load(f)

    # check source script
    src_script_path = config['src_script_file']
    src_font_table_path = config['src_font_table_file']
    if not check_file(src_script_path): return
    if not check_file(src_font_table_path): return

    print (f'check {src_script_path}...')
    with open(src_script_path, 'r') as f:
        scripts = json.load(f)

    font_table, _, _ = read_font_table(src_font_table_path)
    count_false_length, count_false_letters = check_script(scripts, font_table)
    print (f'False sentence length and letter count: {count_false_length}, {count_false_letters}')

    # check destination script
    dst_script_path = config['dst_script_file']
    dst_font_table_path = config['dst_font_table_file']
    if not check_file(dst_script_path): return
    if not check_file(dst_font_table_path): return

    print (f'check {dst_script_path}...')
    with open(dst_script_path, 'r') as f:
        scripts = json.load(f)

    font_table, _, _ = read_font_table(dst_font_table_path)
    count_false_length, count_false_letters = check_script(scripts, font_table)
    print (f'False sentence length and letter count: {count_false_length}, {count_false_letters}')


if __name__ == "__main__":
    main()




