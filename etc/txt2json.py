import json

def main():
    
    src_file_name = '../workspace/S01_C12_jp.txt'
    dst_file_name = src_file_name.replace('.txt', '.json')
    #src_path = f'../workspace/data/script/{src_file_name}'
    #dst_path = f'../workspace/data/script/{dst_file_name}'
    src_path = src_file_name
    dst_path = dst_file_name


    # read text script
    with open(src_path, 'r') as f:
        script_txt = f.read()
    script_txt.strip()
    script_table = script_txt.split('\n')

    # read script
    iteration = (len(script_table)//2)*2 # to remove odd elements

    scripts = dict()

    for i in range(0, iteration, 2):
        # check sentence length
        [code_hex_start, code_hex_end] = script_table[i].split('=')
        key = f'0x{code_hex_start}=0x{code_hex_end}'
        sentence = script_table[i+1]
        scripts[key] = sentence

    # read json script
    with open(dst_path, 'w') as f:
        json.dump(scripts, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
    