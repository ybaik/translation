from pathlib import Path
from module.ozmlib import OZM


def main():
    base_dir = Path("c:/work_han/ozm")

    ref_path = "TAITLE.OZM"
    png_path = "TAITLE.png"

    osm = OZM()
    osm.read_ozm(str(base_dir / ref_path))
    osm.read_png_as_8bpp(str(base_dir / png_path))
    # with open("TAITLE.raw", "wb") as f:
    #     f.write(osm.data_8bpp)
    osm.compress("TAITLE.OZM")


if __name__ == "__main__":
    main()
