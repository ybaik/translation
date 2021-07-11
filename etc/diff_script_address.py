import json

from font_table import check_file, read_font_table

def diff_address(src_scripts, dst_scripts):

    reversed = False
    if len(src_scripts.keys()) >= len(dst_scripts):
        scripts_1 = src_scripts
        scripts_2 = dst_scripts
    else:
        scripts_1 = dst_scripts
        scripts_2 = src_scripts
        reversed = True

    count_diff = 0
    for key, _ in scripts_1.items():
           if scripts_2.get(key) is None:
                if reversed:
                    print(f'Diff = src address [], dst address [{key}]')
                else:
                    print(f'Diff = src address [{key}], dst address []')
                count_diff += 1

    print(f'Number of diff = {count_diff}')


def main():
    # read config
    config_path = 'config.json'
    if not check_file(config_path): return
    with open('config.json') as f:
        config = json.load(f)

    # check source script
    src_script_path = config['src_script_file']

    #src_script_path = '../workspace/FQ3MES_jpn.json'

    if not check_file(src_script_path): return

    print (f'check {src_script_path}...')
    with open(src_script_path, 'r') as f:
        src_scripts = json.load(f)

    # check destination script
    dst_script_path = config['dst_script_file']

    #dst_script_path = '../workspace/FQ3MES_kor.json'


    if not check_file(dst_script_path): return

    print (f'check {dst_script_path}...')
    with open(dst_script_path, 'r') as f:
        dst_scripts = json.load(f)

    diff_address(src_scripts, dst_scripts)


if __name__ == "__main__":
    main()




