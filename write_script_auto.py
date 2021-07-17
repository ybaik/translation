import os
import json
from module.font_table import check_file, FontTable
from check_script import check_script, diff_address


def main():

    src_path = '../workspace/Macross3_jpn'
    dst_path = '../workspace/Macross3_final'
    script_path = '../workspace/Macross3_final/scripts'
    dst_font_table_path = 'font_table/anex86kor.json'

    files = os.listdir(src_path)

    for file in files:

        src_data_path = f'{src_path}/{file}'
        dst_data_path = f'{dst_path}/{file}'

        if not os.path.isfile(src_data_path):
            continue
            
        print(f'{file} ===========================================')

        tag = file.split('.')[0]
        src_script_path = f'{script_path}/{tag}_jpn.json'
        dst_script_path = f'{script_path}/{tag}_kor.json'

        if not os.path.isfile(src_script_path):
            continue
        if not os.path.isfile(dst_script_path):
            continue


        # read scripts
        with open(src_script_path, 'r') as f:
            src_scripts = json.load(f)
        with open(dst_script_path, 'r') as f:
            dst_scripts = json.load(f)

        # read a font table
        if not check_file(dst_font_table_path): return
        font_table = FontTable(dst_font_table_path)

        # check address
        count_diff = diff_address(src_scripts, dst_scripts)
        if count_diff:
            return

        # check scripts
        count_false_length, count_false_letters = check_script(dst_scripts, font_table)
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

        # write scripts
        for range, sentence in dst_scripts.items():
            [code_hex_start, code_hex_end] = range.split('=')
            spos = int(code_hex_start, 16) 
            epos = int(code_hex_end, 16)
            pos = spos
            # write letters in the sentence
            for i, letter in enumerate(sentence):
                if font_table.get_code(letter) is not None:
                    code_hex = font_table.get_code(letter)
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
