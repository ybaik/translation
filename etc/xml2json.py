import os
import json
import xml.etree.ElementTree as ET


def main():
    

    base_path = '../workspace/etc/bgdata'
    files = os.listdir(base_path)

    for file in files:
        if not os.path.isfile(os.path.join(base_path, file)):
            continue
        if file.split('.')[-1] != 'xml':
            continue

        src_file_name = file
        dst_file_name = src_file_name.replace('.xml', '.json')
        src_path = f'../workspace/etc/bgdata/{src_file_name}'
        dst_path = f'../workspace/etc/bgdata/{dst_file_name}'

        # read text script
        script_json = dict()
        root = ET.parse(src_path).getroot()
        for child in root.findall('sentence'):
            start = child.attrib['start']
            end =  child.attrib['end']
            script_json[f'{start}={end}'] = child.text

        # read json script
        with open(dst_path, 'w') as f:
            json.dump(script_json, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()