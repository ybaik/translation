#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image

from end_dat_to_png import (
    BYTES_PER_LINE,
    HALF_HEIGHT,
    HALF_SIZE,
    HEIGHT,
    IMAGE_SIZE,
    PLANE_SIZE,
    WIDTH,
    default_palette_path,
    decode_end_dat,
    load_palette,
    planar_to_indices,
)


def image_number_from_path(path: Path) -> int:
    match = re.search(r"END_S(\d+)", path.stem, re.IGNORECASE)
    if not match:
        raise ValueError(f"cannot infer image number from {path.name}; use --image-number")
    return int(match.group(1))


def image_to_indices(image_path: Path, palette: list[tuple[int, int, int]]) -> bytes:
    image = Image.open(image_path).convert("RGB")
    if image.size != (WIDTH, HEIGHT):
        raise ValueError(f"{image_path} is {image.size}, expected {(WIDTH, HEIGHT)}")

    color_to_index: dict[tuple[int, int, int], int] = {}
    for index, color in enumerate(palette):
        color_to_index.setdefault(color, index)
    pixels = bytearray(WIDTH * HEIGHT)

    for i, color in enumerate(image.getdata()):
        try:
            pixels[i] = color_to_index[color]
        except KeyError as exc:
            x = i % WIDTH
            y = i // WIDTH
            raise ValueError(f"{image_path} pixel ({x}, {y}) color {color} is not in palette") from exc

    return bytes(pixels)


def indices_to_planar(indices: bytes) -> bytes:
    if len(indices) != WIDTH * HEIGHT:
        raise ValueError(f"got {len(indices)} pixels, expected {WIDTH * HEIGHT}")

    vram = bytearray(IMAGE_SIZE)

    for y in range(HEIGHT):
        half = y // HALF_HEIGHT
        y_in_half = y % HALF_HEIGHT
        half_base = half * HALF_SIZE

        for x_byte in range(BYTES_PER_LINE):
            base_pixel = y * WIDTH + x_byte * 8
            for plane in range(4):
                value = 0
                for bit in range(8):
                    color_index = indices[base_pixel + bit]
                    if color_index & (1 << plane):
                        value |= 0x80 >> bit

                vram[half_base + plane * PLANE_SIZE + y_in_half * BYTES_PER_LINE + x_byte] = value

    return bytes(vram)


def encode_rle(vram: bytes) -> bytes:
    if len(vram) != IMAGE_SIZE:
        raise ValueError(f"got {len(vram)} bytes, expected {IMAGE_SIZE}")

    out = bytearray()
    pos = 0
    while pos < len(vram):
        value = vram[pos]
        run_end = pos + 1
        while run_end < len(vram) and vram[run_end] == value:
            run_end += 1

        run_length = run_end - pos
        while run_length > 0:
            if run_length == 1:
                out.append(value)
                run_length -= 1
            else:
                chunk = min(run_length, 257)
                out.extend((value, value, chunk - 2))
                run_length -= chunk

        pos = run_end

    return bytes(out)


def convert(image_path: Path, palette_path: Path, output_path: Path, image_number: int | None = None) -> None:
    if image_number is None:
        image_number = image_number_from_path(image_path)

    palette = load_palette(palette_path, image_number)
    indices = image_to_indices(image_path, palette)
    vram = indices_to_planar(indices)
    encoded = encode_rle(vram)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(IMAGE_SIZE.to_bytes(4, "little") + encoded)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert 640x400 END_S*.png/bmp images to D7END END_S*.DAT.")
    parser.add_argument("image", type=Path, help="Input PNG/BMP image")
    parser.add_argument("output", type=Path, help="Output END_S*.DAT file")
    parser.add_argument("-n", "--image-number", type=int, help="Palette number, e.g. 3 for END_S3")
    parser.add_argument("-p", "--palette", type=Path, help="Palette file. Defaults to data/ENDPAL.GRG, then data/ENDPAL.BRG")
    parser.add_argument("--verify", action="store_true", help="Decode the written DAT and verify it matches the input image indices")
    args = parser.parse_args()

    palette_path = args.palette or default_palette_path(Path("data"))
    image_number = args.image_number if args.image_number is not None else image_number_from_path(args.image)

    convert(args.image, palette_path, args.output, image_number)

    if args.verify:
        palette = load_palette(palette_path, image_number)
        expected = image_to_indices(args.image, palette)
        actual = planar_to_indices(decode_end_dat(args.output))
        if actual != expected:
            raise ValueError(f"verification failed for {args.output}")

    print(args.output)


if __name__ == "__main__":
    main()
