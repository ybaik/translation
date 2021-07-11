import os

def main():
    
    base_path = '../Han/마크로스작업/S1'

    path_list = os.listdir(base_path)

    for f in path_list:
        if not '_jp.txt' in f:
            continue
        # read json script
        with open(f'{base_path}/{f}', 'r') as f:
            scripts = f.readlines()

        print(len(scripts))
        for i, script in enumerate(scripts):
            if 'どうぞ' in script:
                print(f, i, script)


if __name__ == "__main__":
    main()