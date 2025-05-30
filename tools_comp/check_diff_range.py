import os
import json
from pathlib import Path


def check_overlap(ranges, target_range):
    for r in ranges:
        if r[0] <= target_range[1] and r[1] >= target_range[0]:
            return True
    return False


def main():
    base_dir = Path("c:/work_han/workspace")

    ref_dir = base_dir / "patch"
    ref_list = os.listdir(ref_dir)

    src_dir = base_dir / "jpn_all"
    dst_dir = base_dir / "kor_all"

    for ref_file in ref_list:
        src = src_dir / ref_file
        dst = dst_dir / ref_file

        if not src.exists() or not dst.exists():
            print(f"{ref_file} not exist")
            return
        with open(src, "rb") as f:
            src_data = f.read()
        with open(dst, "rb") as f:
            dst_data = f.read()

        if len(src_data) != len(dst_data):
            print(f"{ref_file} diff file size")
            return

        range_list = []

        length = min(len(src_data), len(dst_data))

        start = -1
        for i in range(length):
            if src_data[i] != dst_data[i]:
                if start < 0:
                    start = i
            else: # same byte
                if start >= 0:
                    # check
                    range_list.append([start, i])
                    start = -1
        if len(range_list) == 0:
            continue
        
        # Read code
        json_path = base_dir / f"{ref_file}_kor.json"
        with open(json_path) as f:
            json_data = json.load(f)

        json_data_filtered = dict()

        for k, v in json_data.items():
            buffer_range = k.split("=")
            start = int(buffer_range[0], 16)
            end = int(buffer_range[1], 16)

            is_overlap = check_overlap(range_list, [start, end])
            if is_overlap:
                json_data_filtered[k] = v

        json_path = base_dir / f"{ref_file}_kor_filtered.json"
        with open(json_path, "w") as f:
            json.dump(json_data_filtered, f, ensure_ascii=False, indent=4)
   

if __name__ == '__main__':
    main()
