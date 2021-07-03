import json

def main():
    
    # read json script
    with open('workspace/S01_VIS_jpn.json', 'r') as f:
        scripts_json = json.load(f)

    # read text script
    with open('workspace/S01_VIS_kor.txt', 'r') as f:
        script_txt = f.read()
    script_txt.strip()
    script_table = script_txt.split('\n')

    # read script
    iteration = (len(script_table)//2)*2 # to remove odd elements

    for i in range(0, iteration, 2):
        # check sentence length
        [code_hex_start, code_hex_end] = script_table[i].split('=')
        key = f'0x{code_hex_start}=0x{code_hex_end}'
        sentence = script_table[i+1]

        if scripts_json.get(key):
            if len(scripts_json.get(key)) == len(sentence):
                scripts_json[key] = sentence
            else:
                print(key, sentence, len(scripts_json.get(key)), len(sentence))
        else:
            print(key)

    # read json script
    with open('workspace/S01_VIS_kor.json', 'w') as f:
        json.dump(scripts_json, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()