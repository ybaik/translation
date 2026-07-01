#!/usr/bin/env python3
"""Decode all fixed-size raw planar archives; intermediates are optional."""

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from gspecific.taikou1.pc98_image_codec import decode_planar, write_html_report

JOBS = (
    # ("source/ANIME.PUT", "anime.put.jpn", 16, 16, 3),
    ("source/GRAPH.PUT", "graph.put.jpn", 32, 32, 3),
    # ("source/HEX.PUT", "hex.put.jpn", 40, 24, 3),
    ("source/HIME.PUT", "hime.put.jpn", 64, 80, 3),
    ("source/KAO.PUT", "kao.put.jpn", 64, 80, 3),
    # ("source/MONTA.PUT", "monta.put.jpn", 48, 24, 4),
    # ("source/SAIKORO.PUT", "saikoro.put.jpn", 24, 18, 4),
    # ("source/UNIT.PUT", "unit.put.jpn", 16, 16, 3),
    ("source/PTN.DAT", "ptn.dat.jpn", 32, 32, 3),
)

FRAME_OVERRIDES = {
    "source/GRAPH.PUT": {
        0x000180: (64, 48, 3),
    },
}

EMBEDDED_JOBS = (
    (
        "source/MAIN.EXE",
        "main.exe.jpn",
        ((0x060B90, 32, 32, 3),),
    ),
)


def hex_offset(value):
    return f"0x{value:06X}"


def decode_block(data, offset, width, height, planes):
    if width % 8:
        raise ValueError("width must be divisible by 8")
    size = width * height * planes // 8
    if offset + size > len(data):
        raise EOFError("incomplete PUT block")

    image, _ = decode_planar(data[offset : offset + size], width, height, planes)
    return image, size


def frame_layout(data_size, width, height, planes, overrides=None):
    """Yield mixed-size raw planar frame boundaries, applying offset overrides."""
    overrides = overrides or {}
    offset = 0
    while offset < data_size:
        frame_width, frame_height, frame_planes = overrides.get(
            offset, (width, height, planes)
        )
        frame_size = frame_width * frame_height * frame_planes // 8
        if offset + frame_size > data_size:
            break
        yield offset, frame_width, frame_height, frame_planes, frame_size
        offset += frame_size


def decode_file(
    source,
    output_dir,
    width,
    height,
    planes,
    columns=16,
    scale=1,
    *,
    include_intermediate=False,
    frame_overrides=None,
    frame_ranges=None,
):
    source = Path(source)
    data = source.read_bytes()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    block_size = width * height * planes // 8
    if frame_ranges is None:
        layout = list(frame_layout(len(data), width, height, planes, frame_overrides))
    else:
        layout = [
            (
                offset,
                frame_width,
                frame_height,
                frame_planes,
                frame_width * frame_height * frame_planes // 8,
            )
            for offset, frame_width, frame_height, frame_planes in frame_ranges
        ]
        for offset, _width, _height, _planes, frame_size in layout:
            if offset + frame_size > len(data):
                raise EOFError(f"frame at 0x{offset:06X} extends past {source} EOF")
    count = len(layout)
    consumed = layout[-1][0] + layout[-1][4] if layout else 0
    remainder = 0 if frame_ranges is not None else len(data) - consumed
    sheet_frames = []
    report_frames = []
    for index, (offset, frame_width, frame_height, frame_planes, frame_size) in enumerate(layout):
        next_offset = offset + frame_size
        stem = f"{offset:06X}"
        planar = data[offset:next_offset]
        image, pixels = decode_planar(
            planar, frame_width, frame_height, frame_planes
        )
        plane_name = f"{stem}.plane.raw"
        png_name = f"{stem}.png"
        (output / plane_name).write_bytes(planar)
        image.save(output / png_name)
        sheet_frames.append(image.convert("RGB"))
        report_frames.append(
            {
                "index": index,
                "offset": hex_offset(offset),
                "next_offset": hex_offset(next_offset),
                "plane_size": frame_size,
                "width": frame_width,
                "height": frame_height,
                "planes": frame_planes,
                "files": {
                    "plane": plane_name,
                    "png": png_name,
                },
            }
        )
        if include_intermediate:
            pixels_name = f"{stem}.pixels.raw"
            (output / pixels_name).write_bytes(pixels)
            report_frames[-1]["files"]["pixels"] = pixels_name

    rows = math.ceil(count / columns)
    label_height = 10
    max_width = max(image.width for image in sheet_frames)
    max_height = max(image.height for image in sheet_frames)
    cell_width = max_width * scale
    cell_height = max_height * scale + label_height
    sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), (32, 32, 32))
    draw = ImageDraw.Draw(sheet)
    for index, image in enumerate(sheet_frames):
        x = (index % columns) * cell_width
        y = (index // columns) * cell_height
        if scale != 1:
            image = image.resize(
                (image.width * scale, image.height * scale), Image.Resampling.NEAREST
            )
        image_x = x + (cell_width - image.width) // 2
        sheet.paste(image, (image_x, y))
        draw.text((x, y + max_height * scale), str(index), fill=(255, 255, 255))
    sheet.save(output / "sheet.png")

    report = {
        "source": str(source),
        "format": f"raw {planes}bpp planar B/R/G" + ("/I" if planes == 4 else ""),
        "block_size": block_size,
        "frames": report_frames,
    }
    if remainder:
        report["incomplete"] = {
            "offset": hex_offset(consumed),
            "remaining_bytes": remainder,
        }
    (output / "index.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_html_report(report, output)
    return count, remainder, block_size


def main():
    parser = argparse.ArgumentParser(
        description="Decode fixed-size raw planar archives"
    )
    parser.add_argument(
        "--intermediate",
        action="store_true",
        help="also save decoded pixels.raw intermediate files",
    )
    args = parser.parse_args()
    for source, output_dir, width, height, planes in JOBS:
        frame_overrides = FRAME_OVERRIDES.get(source)
        count, remainder, block_size = decode_file(
            source,
            output_dir,
            width,
            height,
            planes,
            include_intermediate=args.intermediate,
            frame_overrides=frame_overrides,
        )
        print(
            f"{source}: decoded={count} remainder={remainder} "
            f"block_size={block_size} output={output_dir}"
        )
    for source, output_dir, frame_ranges in EMBEDDED_JOBS:
        width, height, planes = frame_ranges[0][1:]
        count, remainder, block_size = decode_file(
            source,
            output_dir,
            width,
            height,
            planes,
            include_intermediate=args.intermediate,
            frame_ranges=frame_ranges,
        )
        print(
            f"{source}: decoded={count} embedded frame(s) "
            f"block_size={block_size} output={output_dir}"
        )


if __name__ == "__main__":
    main()
