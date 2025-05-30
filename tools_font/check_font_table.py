import json
from pathlib import Path


def main():
    base_path = Path("c:/work_han")
    json_path = base_path / "font_table-kor-jin-pd.json"
    tbl_path = base_path / "font_table-kor-jin-pd.tbl"
    
    with open(json_path, "r") as f:
        font_table = json.load(f)
    
    with open(tbl_path, "r") as f:
        tbl = f.readlines()
    
    if len(tbl) != len(font_table.keys()):
        print("tbl length is not equal to font_table length")
        return
    
    for info in tbl:
        info = info.strip()
        idx = info.find("=")
        code = info[:idx]
        char = info[idx+1:]

        if code not in font_table:
            print(f"code {code} not found in font_table")
            return
        char_ = font_table.get(code)

        if char != char_:
            print(f"char {char} not found in font_table")
            return
    print("json and tbl are same.")

if __name__ == '__main__':
    main()
