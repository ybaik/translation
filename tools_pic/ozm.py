from pathlib import Path
from module.ozmlib import OZM


def main():
    base_dir = Path("c:/work_han/ozm")
    ref_base_dir = Path("c:/work_han/workspace7/kor/mac2")
    target_dir = base_dir / "m2_kor"

    for file in target_dir.rglob("*.png"):
        relative_path = file.relative_to(target_dir)

        out_path = target_dir / relative_path.with_suffix(".OZM")
        if out_path.exists():
            continue

        target_path = ref_base_dir / relative_path.with_suffix(".OZM")
        if not target_path.exists():
            print(f"{out_path.name} is not exists.")
            continue

        osm = OZM()
        osm.read_ozm(target_path)
        osm.read_png_as_8bpp(file)
        # with open("TAITLE.raw", "wb") as f:
        #     f.write(osm.data_8bpp)
        osm.compress(out_path)


if __name__ == "__main__":
    main()
