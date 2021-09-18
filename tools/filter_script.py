import os
import json

def main():

    file_path = '../workspace/S02_R01_kor.json'

    with open(file_path, 'r') as f:
        scripts = json.load(f)

    scripts_new = dict()

    for key, val in scripts.items():
        if val != '@':
            scripts_new[key] = val

    with open(file_path, 'w') as f:
         json.dump(scripts_new, f, ensure_ascii=False, indent=4)


    




if __name__ == "__main__":
    main()