#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image

from gspecific.image_workspace import ImageWorkspace, native_artifact_name, update_meta
from module.pc98_image.planar import encode_plane_major_row_planar

from gspecific.garyou.end_dat_to_png import (
    HALF_HEIGHT,
    HEIGHT,
    IMAGE_SIZE,
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

    half_pixels = WIDTH * HALF_HEIGHT
    return b"".join(
        encode_plane_major_row_planar(
            indices[offset : offset + half_pixels], WIDTH, HALF_HEIGHT, 4
        )
        for offset in (0, half_pixels)
    )


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


def encode_workspace_file(
    source_path: Path,
    image_path: Path,
    palette_path: Path,
    output_dir: Path,
    image_number: int | None = None,
) -> Path:
    if image_number is None:
        image_number = image_number_from_path(source_path)

    palette = load_palette(palette_path, image_number)
    indices = image_to_indices(image_path, palette)
    vram = indices_to_planar(indices)
    encoded = IMAGE_SIZE.to_bytes(4, "little") + encode_rle(vram)
    stem = source_path.stem
    output_path = output_dir / native_artifact_name(source_path.name, "kor")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{stem}.idx.kor.bin").write_bytes(indices)
    (output_dir / f"{stem}.pln.kor.bin").write_bytes(vram)
    output_path.write_bytes(encoded)
    update_meta(
        output_dir / f"{stem}.meta.json",
        encoded_size=len(encoded),
        stored_size=len(encoded),
        padding_byte=None,
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert 640x400 END_S*.png/bmp images to D7END END_S*.DAT.")
    parser.add_argument(
        "--workspace",
        required=True,
        type=Path,
        help="workspace containing jpn-pc98 and image-pc98",
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="source filenames relative to jpn-pc98; defaults to END_S*.DAT",
    )
    parser.add_argument(
        "-p",
        "--palette",
        type=Path,
        help="palette path; defaults to ENDPAL.GRG/BRG in jpn-pc98",
    )
    parser.add_argument("--verify", action="store_true", help="Decode the written DAT and verify it matches the input image indices")
    args = parser.parse_args()

    workspace = ImageWorkspace(args.workspace)
    sources = (
        [workspace.source(path) for path in args.inputs]
        if args.inputs
        else sorted(workspace.source_root.glob("END_S*.DAT"), key=image_number_from_path)
    )
    palette_path = args.palette or default_palette_path(workspace.source_root)

    for source_path in sources:
        image_number = image_number_from_path(source_path)
        output_dir = workspace.artifacts(source_path.relative_to(workspace.source_root))
        image_path = output_dir / f"{source_path.stem}.kor.png"
        if not image_path.exists():
            print(f"skip: {image_path} does not exist")
            continue
        output_path = encode_workspace_file(
            source_path,
            image_path,
            palette_path,
            output_dir,
            image_number,
        )

        if args.verify:
            palette = load_palette(palette_path, image_number)
            expected = image_to_indices(image_path, palette)
            actual = planar_to_indices(decode_end_dat(output_path))
            if actual != expected:
                raise ValueError(f"verification failed for {output_path}")

        print(output_path)


if __name__ == "__main__":
    main()
