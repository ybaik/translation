#!/usr/bin/env python3
"""Decode the game's RLE/LZ image archives; intermediates are optional."""

import argparse
import json
from pathlib import Path

from gspecific.taikou1.pc98_image_codec import decode_rle_lz, write_html_report


JOBS = (
    ("source/OPEN.DAT", "open.dat.jpn", False),
    ("source/END.DAT", "end.dat.jpn", True),
    ("source/GRAPH.DAT", "graph.dat.jpn", False),
    ("source/EV_PIC.DAT", "ev_pic.dat.jpn", False),
    # ("source/INT_BAK.NPK", "int_bak.npk.jpn", False),
)


def hex_offset(value):
    return f"0x{value:06X}"


def decode_file(
    source,
    output_dir,
    *,
    offset_names=False,
    allow_incomplete=False,
    include_intermediate=False,
):
    data = Path(source).read_bytes()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    frames = []
    incomplete = None
    offset = 0
    while offset < len(data):
        try:
            image, planar, pixels, info = decode_rle_lz(data, offset)
        except EOFError as error:
            if not allow_incomplete:
                raise
            incomplete = {
                "offset": offset,
                "remaining_bytes": len(data) - offset,
                "error": str(error),
            }
            break
        index = len(frames)
        stem = f"{offset:06X}" if offset_names else f"{index:03d}_{offset:06X}"
        compressed = data[offset : info["next_offset"]]
        compressed_name = f"{stem}.rle_lz.bin"
        (output / compressed_name).write_bytes(compressed)
        image.save(output / f"{stem}.png")
        info["files"] = {
            "compressed": compressed_name,
            "png": f"{stem}.png",
        }
        if include_intermediate:
            plane_name = f"{stem}.plane.raw"
            pixels_name = f"{stem}.pixels.raw"
            (output / plane_name).write_bytes(planar)
            (output / pixels_name).write_bytes(pixels)
            info["files"]["plane"] = plane_name
            info["files"]["pixels"] = pixels_name
        frames.append(info)
        offset = info["next_offset"]
    report_frames = []
    for frame in frames:
        report_frame = dict(frame)
        report_frame["offset"] = hex_offset(frame["offset"])
        report_frame["next_offset"] = hex_offset(frame["next_offset"])
        report_frames.append(report_frame)
    report = {"source": str(source), "frames": report_frames}
    if incomplete:
        report["incomplete"] = {
            **incomplete,
            "offset": hex_offset(incomplete["offset"]),
        }
    (output / "index.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_html_report(report, output)
    return frames


def main():
    parser = argparse.ArgumentParser(
        description="Decode the game's RLE/LZ image archives"
    )
    parser.add_argument(
        "--intermediate",
        action="store_true",
        help="also save decoded plane.raw and pixels.raw intermediate files",
    )
    args = parser.parse_args()
    for source, output_dir, allow_incomplete in JOBS:
        frames = decode_file(
            source,
            output_dir,
            offset_names=True,
            allow_incomplete=allow_incomplete,
            include_intermediate=args.intermediate,
        )
        print(f"{source}: decoded={len(frames)} output={output_dir}")


if __name__ == "__main__":
    main()
