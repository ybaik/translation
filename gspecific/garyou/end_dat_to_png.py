#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PIL import Image

from module.pc98_image.palette import decode_4bit_palette
from module.pc98_image.planar import decode_plane_major_row_planar

WIDTH = 640
HEIGHT = 400
HALF_HEIGHT = 200
BYTES_PER_LINE = WIDTH // 8
PLANE_SIZE = BYTES_PER_LINE * HALF_HEIGHT
HALF_SIZE = PLANE_SIZE * 4
IMAGE_SIZE = HALF_SIZE * 2


def decode_end_dat(dat_path: Path) -> bytes:
    src = dat_path.read_bytes()
    if len(src) < 4:
        raise ValueError(f"{dat_path} is too small")

    # D7END.EXE sub_10B00 seeks to offset 4, then sub_10A92 expands this RLE.
    src_pos = 4
    dst = bytearray(IMAGE_SIZE)
    dst_pos = 0

    while src_pos < len(src) and dst_pos < IMAGE_SIZE:
        value = src[src_pos]
        src_pos += 1
        dst[dst_pos] = value
        dst_pos += 1

        while src_pos < len(src) and dst_pos < IMAGE_SIZE:
            run_value = value
            value = src[src_pos]
            src_pos += 1
            dst[dst_pos] = value
            dst_pos += 1

            if value != run_value:
                continue

            if src_pos >= len(src):
                break

            count = src[src_pos]
            src_pos += 1
            if count:
                end = min(dst_pos + count, IMAGE_SIZE)
                dst[dst_pos:end] = bytes([run_value]) * (end - dst_pos)
                dst_pos += count
            break

    if dst_pos < IMAGE_SIZE:
        print(
            f"warning: {dat_path} decoded to {dst_pos} bytes; padding to {IMAGE_SIZE} with color 0",
            file=sys.stderr,
        )
    elif dst_pos > IMAGE_SIZE:
        raise ValueError(f"{dat_path} decoded to {dst_pos} bytes, expected {IMAGE_SIZE}")

    return bytes(dst)


def load_palette(palette_path: Path, image_number: int) -> list[tuple[int, int, int]]:
    data = palette_path.read_bytes()
    palette_count = len(data) // (16 * 3)
    palette_index = image_number - 1
    if palette_index < 0 or palette_index >= palette_count:
        raise ValueError(f"palette #{image_number} is not present in {palette_path}")

    offset = palette_index * 16 * 3
    return list(decode_4bit_palette(data[offset : offset + 48], order="brg"))


def planar_to_indices(vram: bytes) -> bytes:
    if len(vram) != IMAGE_SIZE:
        raise ValueError(f"got {len(vram)} planar bytes, expected {IMAGE_SIZE}")
    return b"".join(
        decode_plane_major_row_planar(
            vram[offset : offset + HALF_SIZE], WIDTH, HALF_HEIGHT, 4
        )
        for offset in (0, HALF_SIZE)
    )


def image_number_from_path(path: Path) -> int:
    match = re.search(r"END_S(\d+)\.DAT$", path.name, re.IGNORECASE)
    if not match:
        raise ValueError(f"cannot infer image number from {path.name}")
    return int(match.group(1))


def convert(dat_path: Path, palette_path: Path, output_path: Path, image_number: int | None = None) -> None:
    if image_number is None:
        image_number = image_number_from_path(dat_path)

    vram = decode_end_dat(dat_path)
    indices = planar_to_indices(vram)
    colors = load_palette(palette_path, image_number)

    rgb = bytearray(WIDTH * HEIGHT * 3)
    for i, color_index in enumerate(indices):
        rgb[i * 3 : i * 3 + 3] = bytes(colors[color_index])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.frombytes("RGB", (WIDTH, HEIGHT), bytes(rgb)).save(output_path)


def default_palette_path(data_dir: Path) -> Path:
    for name in ("ENDPAL.GRG", "ENDPAL.BRG"):
        path = data_dir / name
        if path.exists():
            return path
    raise FileNotFoundError(f"cannot find ENDPAL.GRG or ENDPAL.BRG in {data_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert D7END END_S*.DAT images to PNG.")
    parser.add_argument("inputs", nargs="*", type=Path, help="END_S*.DAT files. Defaults to data/END_S*.DAT")
    parser.add_argument("-p", "--palette", type=Path, help="Palette file. Defaults to data/ENDPAL.GRG, then data/ENDPAL.BRG")
    parser.add_argument("-o", "--out-dir", type=Path, default=Path("out"), help="Output directory")
    args = parser.parse_args()

    inputs = args.inputs or sorted(Path("data").glob("END_S*.DAT"), key=image_number_from_path)
    palette_path = args.palette or default_palette_path(Path("data"))

    for dat_path in inputs:
        out_path = args.out_dir / f"{dat_path.stem}.png"
        convert(dat_path, palette_path, out_path)
        print(out_path)


if __name__ == "__main__":
    main()
