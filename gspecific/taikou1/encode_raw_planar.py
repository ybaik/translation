#!/usr/bin/env python3
"""Encode offset-named PNG files in matching .kor folders as raw planar blocks."""

import json
from pathlib import Path

from gspecific.taikou1.decode_raw_planar import (
    EMBEDDED_JOBS,
    FRAME_OVERRIDES,
    JOBS,
    frame_layout,
)
from gspecific.taikou1.pc98_image_codec import image_to_planar


def hex_offset(value):
    return f"0x{value:06X}"


def offset_pngs(directory):
    for path in sorted(directory.glob("*.png")):
        try:
            offset = int(path.stem, 16)
        except ValueError:
            continue
        yield offset, path


def encode_folder(
    source,
    jpn_dir,
    width,
    height,
    planes,
    *,
    frame_overrides=None,
    frame_ranges=None,
):
    kor_dir = Path(str(jpn_dir).removesuffix(".jpn") + ".kor")
    if not kor_dir.is_dir():
        print(f"skip: {kor_dir} does not exist")
        return 0

    source_path = Path(source)
    source_size = source_path.stat().st_size
    block_size = width * height * planes // 8
    if frame_ranges is None:
        layout = {
            offset: (frame_width, frame_height, frame_planes, frame_size)
            for offset, frame_width, frame_height, frame_planes, frame_size in frame_layout(
                source_size, width, height, planes, frame_overrides
            )
        }
    else:
        layout = {
            offset: (
                frame_width,
                frame_height,
                frame_planes,
                frame_width * frame_height * frame_planes // 8,
            )
            for offset, frame_width, frame_height, frame_planes in frame_ranges
        }
    entries = []
    for offset, png_path in offset_pngs(kor_dir):
        if offset not in layout:
            raise ValueError(f"{png_path}: offset is not a known frame boundary")
        frame_width, frame_height, frame_planes, frame_size = layout[offset]

        encoded, _pixels = image_to_planar(
            png_path, frame_width, frame_height, frame_planes
        )
        output_name = f"{offset:06X}.plane.raw"
        (kor_dir / output_name).write_bytes(encoded)
        entries.append(
            {
                "offset": hex_offset(offset),
                "next_offset": hex_offset(offset + frame_size),
                "width": frame_width,
                "height": frame_height,
                "planes": frame_planes,
                "encoded_size": len(encoded),
                "files": {"png": png_path.name, "encoded": output_name},
            }
        )
        print(f"{png_path}: encoded={len(encoded)}")

    report = {
        "source": str(source_path),
        "format": f"raw {planes}bpp planar B/R/G" + ("/I" if planes == 4 else ""),
        "block_size": block_size,
        "entries": entries,
    }
    (kor_dir / "encode_index.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{kor_dir}: encoded={len(entries)}")
    return len(entries)


def main():
    for source, jpn_dir, width, height, planes in JOBS:
        encode_folder(
            source,
            jpn_dir,
            width,
            height,
            planes,
            frame_overrides=FRAME_OVERRIDES.get(source),
        )
    for source, jpn_dir, frame_ranges in EMBEDDED_JOBS:
        width, height, planes = frame_ranges[0][1:]
        encode_folder(
            source,
            jpn_dir,
            width,
            height,
            planes,
            frame_ranges=frame_ranges,
        )


if __name__ == "__main__":
    main()
