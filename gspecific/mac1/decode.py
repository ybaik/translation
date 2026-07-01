import cv2
import struct
import numpy as np
from pathlib import Path
from module.pc98_image.planar import decode_plane_major_row_planar


def read_img(file_path: Path) -> tuple:
    """
    Reads a .IMG file and returns the tag, width, height, and compresssed_data data.
    """
    with open(file_path, "rb") as f:
        tag, w, h = struct.unpack("<HHH", f.read(6))
        compresssed_data = bytearray(f.read())
    return tag, (w + 1) * 8, h + 1, compresssed_data


def decompress_img(raw: bytearray, width: int, height: int) -> bytearray:
    """
    Decompresses a .IMG file and returns the decompressed data.
    """
    width_4bpp = width // 8
    w = width_4bpp - 1
    h = height - 1

    planar_data = bytearray(height * width_4bpp * 4)

    buf_return = (h) * width_4bpp
    raw_idx = 0
    buf_idx = 0
    h_idx = h
    w_idx = w
    ah = 0

    while raw_idx < len(raw):
        al = raw[raw_idx]
        raw_idx += 1
        if al != 0:  # Direct update
            ah = ah ^ al  # to keep delta value instead of absolute value
            planar_data[buf_idx] = ah

            # Check boundary conditions
            if h_idx < 1:
                buf_idx -= buf_return
                buf_idx += 1
                w_idx -= 1
                h_idx = h
            else:
                buf_idx += width_4bpp
                h_idx -= 1
            if w_idx < 0:
                w_idx = w
                buf_idx += buf_return
        else:  # RLE decoding when al == 0
            al = raw[raw_idx]
            raw_idx += 1

            if al == 0:  # bl is big...
                al = raw[raw_idx]
                raw_idx += 1
                bl = al
                al = raw[raw_idx]
                raw_idx += 1
                bl += al * 256
            else:  # al != 0
                bl = al
            for k in range(bl):
                planar_data[buf_idx] = ah

                # Check boundary conditions
                if h_idx < 1:
                    buf_idx -= buf_return
                    buf_idx += 1
                    w_idx -= 1
                    h_idx = h
                else:
                    buf_idx += width_4bpp
                    h_idx -= 1
                if w_idx < 0:
                    w_idx = w
                    buf_idx += buf_return

    return planar_data


def main():
    DEBUG = False
    base_dir = Path("customized/mac1/examples")
    file_path = base_dir / "MG09.IMG"

    if "MG09.IMG" in str(file_path):
        DEBUG = True
        with open(base_dir / "MG09.PLA", "rb") as f:
            reference = f.read()
    try:
        tag, width, height, compresssed_data = read_img(file_path)
    except FileNotFoundError:
        print(f"Error: Input file not found at {file_path}")
        return

    planar_data = decompress_img(compresssed_data, width, height)

    if DEBUG and bytearray(reference) != planar_data:
        ValueError("Value error")
    else:
        print("success")

    # --- Start of added code (Using Standard Planar Conversion) ---
    try:
        print(f"Processing {width}x{height} image (Standard Planar)...")

        # Convert the planar data in planar_data to a standard 8bpp indexed ("chunky") format.
        indexed_8bpp_data = decode_plane_major_row_planar(
            planar_data, width, height, 4
        )

        # Create a NumPy array from the converted 1D data and reshape it to a 2D image.
        image_indexed_2d = np.frombuffer(indexed_8bpp_data, dtype=np.uint8).reshape((height, width))

        # Convert the 4-bit indexed image (values 0-15) to an 8bpp grayscale image (values 0-255).
        image_8bpp_grayscale = (image_indexed_2d * 17).astype(np.uint8)

        output_filename = str(file_path).replace(".IMG", ".BMP")
        cv2.imwrite(output_filename, image_8bpp_grayscale)
        print(f"Successfully decoded and saved to {output_filename}")

    except NameError:
        print("\n---")
        print("Could not process image because 'cv2' or 'numpy' module is not available.")
        print("Please install 'opencv-python' and 'numpy' using: pip install opencv-python numpy")
    except Exception as e:
        print(f"\nAn error occurred while processing the image: {e}")
        import traceback

        traceback.print_exc()
        print("Please check if 'w' and 'h' are loaded correctly and 'buf_4bpp' has enough data.")
    # --- End of added code ---


if __name__ == "__main__":
    main()
