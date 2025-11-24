from pathlib import Path
from module.ozmlib import OZM

m2_list = ["STR_MENU.OZM", "TAC_MENU.OZM"]
m3_list = []
m4_list = []


def main():
    base_dir = Path("C:/work_han/ozm")
    out_base_dir = Path("C:/work_han/ozm")

    osm = OZM()
    for file in base_dir.glob("*.OZM"):
        out_name = file.name.replace(".OZM", ".png")
        out_path = out_base_dir / out_name

        if out_path.exists():
            continue

        if file.name in m2_list:
            continue
        print(file.name)
        # file = Path("BAT_MENU.OZM")

        osm.read_ozm(file)
        osm.decompress()
        # with open("BAT_MENU.raw", "wb") as f:
        #     f.write(osm.data_8bpp)
        osm.save_as_png(out_path)


if __name__ == "__main__":
    main()
