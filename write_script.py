import json
from font_table import check_file, read_font_table
from check_script import check_script


def main():

    config_path = 'config.json'
    if not check_file(config_path): return
    with open('config.json') as f:
        config = json.load(f)

    dst_font_table_path = config['dst_font_table_file']
    dst_script_path = config['dst_script_file']
    src_data_path = config['src_data_file']
    dst_data_path = config['dst_data_file']

    # read scripts
    with open(dst_script_path, 'r') as f:
        scripts = json.load(f)

    # read a font table
    if not check_file(dst_font_table_path): return
    font_table, _, _ = read_font_table(dst_font_table_path)

    # check scripts
    count_false_length, count_false_letters = check_script(scripts, font_table)
    print (f'False sentence length and letter count: {count_false_length}, {count_false_letters}')

    if count_false_length or count_false_letters:
        print('False sentence length or letters should be fixed.')
        return

    # read the target (jpn) data
    if not check_file(src_data_path): return
    with open(src_data_path, 'rb') as f:
        data = f.read()
    data = bytearray(data)        
    print(f'Data size: {src_data_path}({len(data):,} bytes)')

    # make a letter to code table
    letter_to_code = dict()
    for k, v in font_table.items():
        if letter_to_code.get(v) is None:
            letter_to_code[v] = k

    # write scripts
    for range, sentence in scripts.items():
        [code_hex_start, code_hex_end] = range.split('=')
        spos = int(code_hex_start, 16) 
        epos = int(code_hex_end, 16)
        pos = spos
        # write letters in the sentence
        for i, letter in enumerate(sentence):
            if letter_to_code.get(letter) is not None:
                code_hex = letter_to_code.get(letter)                
                code_int = int(code_hex, 16)

                code1 = (code_int & 0xff00) >> 8
                code2 = (code_int & 0x00ff)
                data[pos] = code1
                data[pos+1] = code2
            else:
                assert 0, f'{letter} is not in the font table.'
            pos += 2

    # save data
    with open(dst_data_path, 'wb') as f:
        f.write(data)


if __name__ == "__main__":
    main()
