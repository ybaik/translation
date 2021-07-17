import json
from module.font_table import check_file, FontTable


def main():

    # read a config file
    config_path = 'config.json'
    if not check_file(config_path): return 
    with open(config_path) as f:
        config = json.load(f)

    # read data paths
    src_data_path = config['src_data_file']
    src_font_table_path = config['src_font_table_file']
    src_script_path = config['src_script_file']

    # read a threshold
    length_threshold = config['length_threshold']

    # read a font table
    if not check_file(src_font_table_path): return
    font_table = FontTable(src_font_table_path)

    # read the target (jpn) data
    if not check_file(src_data_path): return
    with open(src_data_path, 'rb') as f: 
        data = f.read()
    print(f'Data size: {src_data_path}({len(data):,} bytes)')

    # extract scripts
    i=0
    length = 0 # sentence length
    sentence = ''
    sentence_log = ''
    script = dict()
    script_log = dict()

    while i < len(data)-1:
        # extract a 2byte code
        code_int = (data[i]<<8) + data[i+1]
        code_hex = hex(code_int)

        # check if value is in range of the source font table
        if font_table.range(code_int):
            # find a character in the font table
            character = font_table.get_char(code_hex)

            if character: # character is in the font table
                sentence += character
                if character == '■': 
                    sentence_log += f':{code_hex}' if sentence_log else f'{code_hex}'
                length += 1
                i += 1
            else: # character is not in the font table
                sentence += '@'
                sentence_log += f':@{code_hex}' if sentence_log else f'@{code_hex}'
                length += 1
                i += 1
        else:
            # check sentence length and save
            if length >= length_threshold:
                address = f'{hex(i-length*2)}={hex(i-1)}'
                script[address] = sentence
                if sentence_log:
                    script_log[address] = sentence_log
            sentence = ''
            sentence_log = ''
            length = 0
        i += 1

    # check a result of the end of data
    if length >= length_threshold:
        address = f'{hex(i-length*2)}={hex(i-1)}'
        script[address] = sentence
        if sentence_log:
            script_log[address] = sentence_log
        sentence = ''
        sentence_log = ''
        length = 0

    # save the extracted scripts
    with open(src_script_path, 'w') as f:
       json.dump(script, f, ensure_ascii=False, indent=4)

    # save logs
    with open('script_log.json', 'w') as f:
       json.dump(script_log, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
