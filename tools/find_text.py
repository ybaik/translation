import os
import json

def main():
    
    base_path = '../workspace/Macross3_final/scripts/s01'
    #base_path = '../workspace'
    path_list = os.listdir(base_path)

    sentence_to_find = '숙소'

    for file in path_list:
        if not '_kor.json' in file:
            continue
        # read json script
        print(file)
        with open(f'{base_path}/{file}', 'r') as f:
            scripts = json.load(f)
        for k, v in scripts.items():
            if sentence_to_find in v:
                print(f'found a candidate file: {file}')


if __name__ == "__main__":
    main()