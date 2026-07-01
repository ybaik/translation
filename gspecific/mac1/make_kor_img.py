# Description: Converts specific grayscale BMP files to the custom compressed IMG format.
# Requirements: opencv-python, numpy
# Usage: python3 make_kor_img.py

import cv2
import struct
from pathlib import Path
from module.pc98_image.planar import encode_plane_major_row_planar

# Import the compression logic from the previously created comp.py
from gspecific.mac1.codec import compress_mac1, generate_traversal_order


def process_image(base_name: str, base_dir: Path):
    """
    Reads a _Kor.bmp, converts, compresses, and saves it as a _Kor.IMG.
    """
    kor_bmp_path = base_dir / f"{base_name}_Kor.bmp"
    original_img_path = base_dir / f"{base_name}.IMG"
    output_img_path = base_dir / f"{base_name}_Kor.IMG"

    print(f"--- Processing {base_name} ---")

    # 1. Read header and dimensions from original .IMG file
    print(f"Reading header from: {original_img_path}")
    try:
        with open(original_img_path, "rb") as f:
            header = f.read(6)
            tag, w, h = struct.unpack("<HHH", header)
    except FileNotFoundError:
        print(f"Error: Original IMG file not found at {original_img_path}")
        return

    print(f"Dimensions from header: w={w}, h={h}")

    # 2. Read the grayscale BMP image
    print(f"Reading grayscale image: {kor_bmp_path}")
    try:
        gray_image = cv2.imread(str(kor_bmp_path), cv2.IMREAD_GRAYSCALE)
        if gray_image is None:
            raise FileNotFoundError
    except FileNotFoundError:
        print(f"Error: Grayscale BMP not found at {kor_bmp_path}")
        return
    except Exception as e:
        print(f"Error reading with OpenCV: {e}. Is opencv-python installed?")
        return

    # 3. Convert 8-bit grayscale (0-255) to 4-bit indices (0-15)
    print("Converting image to 4-bit indices...")
    data_8bpp = gray_image // 17

    # Check dimensions. The image dimensions should match the header info.
    # IMG dimensions are (w+1)*8 by (h+1)
    expected_height = h + 1
    expected_width = (w + 1) * 8
    if gray_image.shape[0] != expected_height or gray_image.shape[1] != expected_width:
        print(
            f"Warning: Image dimensions ({gray_image.shape[1]}x{gray_image.shape[0]}) do not match expected ({expected_width}x{expected_height})"
        )

    # 4. Convert indexed image to 4BPP planar format
    print("Converting to 4BPP planar format...")
    planar_data = encode_plane_major_row_planar(
        data_8bpp.tobytes(), expected_width, expected_height, 4
    )

    # 5. Generate traversal order for compression
    print("Generating traversal order...")
    traversal_indices = generate_traversal_order(w, h)

    # 6. Compress the planar data
    print("Compressing data...")
    compressed_data = compress_mac1(planar_data, traversal_indices)
    print(f"Compression complete. Compressed size: {len(compressed_data)} bytes.")

    # 7. Write the new .IMG file
    print(f"Writing new file: {output_img_path}")
    with open(output_img_path, "wb") as f:
        f.write(header)
        f.write(compressed_data)

    print(f"[SUCCESS] Successfully created {output_img_path}\n")


def main():
    try:
        import cv2
        import numpy
    except ImportError:
        print("Error: 'opencv-python' and 'numpy' are required for this script.")
        print("Please install them using: pip install opencv-python numpy")
        return

    base_dir = Path("customized/mac1/examples")
    files_to_process = ["STA", "MOP"]

    for base_name in files_to_process:
        process_image(base_name, base_dir)


if __name__ == "__main__":
    main()
