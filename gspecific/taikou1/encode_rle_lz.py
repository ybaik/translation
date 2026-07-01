#!/usr/bin/env python3
"""Encode offset-named PNG files in matching .kor folders as RLE/LZ blocks."""

import argparse
import json
from pathlib import Path

from PIL import Image

from gspecific.taikou1.decode_rle_lz import JOBS
from gspecific.taikou1.pc98_image_codec import decode_rle_lz, encode_rle_lz_image


def hex_offset(value):
    return f"0x{value:06X}"


def offset_pngs(directory):
    for path in sorted(directory.glob("*.png")):
        try:
            offset = int(path.stem, 16)
        except ValueError:
            continue
        yield offset, path


def encode_folder(source, jpn_dir, *, padding=False):
    kor_dir = Path(str(jpn_dir).removesuffix(".jpn") + ".kor")
    if not kor_dir.is_dir():
        print(f"skip: {kor_dir} does not exist")
        return 0

    source_path = Path(source)
    source_data = source_path.read_bytes()
    entries = []
    for offset, png_path in offset_pngs(kor_dir):
        _, _, _, original = decode_rle_lz(source_data, offset)
        with Image.open(png_path) as image:
            if image.size != (original["width"], original["height"]):
                raise ValueError(
                    f"{png_path}: got {image.width}x{image.height}, expected "
                    f"{original['width']}x{original['height']}"
                )
        encoded = encode_rle_lz_image(png_path)
        fits_original = len(encoded) <= original["compressed_size"]
        if padding and not fits_original:
            raise ValueError(
                f"{png_path}: encoded block {len(encoded)} exceeds original size "
                f"{original['compressed_size']}; cannot pad to a smaller size"
            )

        padding_size = original["compressed_size"] - len(encoded) if padding else 0
        output_data = encoded + b"\x00" * padding_size
        suffix = ".rle_lz.padded.bin" if padding else ".rle_lz.bin"
        output_name = f"{offset:06X}{suffix}"
        (kor_dir / output_name).write_bytes(output_data)
        entry = {
            "offset": hex_offset(offset),
            "original_next_offset": hex_offset(original["next_offset"]),
            "width": original["width"],
            "height": original["height"],
            "original_size": original["compressed_size"],
            "encoded_size": len(encoded),
            "padding_size": padding_size,
            "padding_byte": "0x00" if padding_size else None,
            "output_size": len(output_data),
            "padded": padding,
            "fits_original": fits_original,
            "files": {"png": png_path.name, "encoded": output_name},
        }
        entries.append(entry)
        print(
            f"{png_path}: encoded={len(encoded)} padding={padding_size} "
            f"output={len(output_data)} original={original['compressed_size']} "
            f"fits={fits_original}"
        )

    report = {
        "source": str(source_path),
        "format": "RLE/LZ-compressed 3bpp B/R/G with width/height header",
        "padding": padding,
        "entries": entries,
    }
    (kor_dir / "encode_index.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{kor_dir}: encoded={len(entries)}")
    return len(entries)


def main():
    parser = argparse.ArgumentParser(
        description="Encode PNG replacements as insertion-ready RLE/LZ blocks"
    )
    parser.add_argument(
        "--padding",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="append 0x00 bytes up to each original compressed block size (default: enabled)",
    )
    args = parser.parse_args()
    for source, jpn_dir, _allow_incomplete in JOBS:
        encode_folder(source, jpn_dir, padding=args.padding)


if __name__ == "__main__":
    main()
