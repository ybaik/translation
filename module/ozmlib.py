# algorithm from https://gitlab.com/bunnylin/supersakura/-/blob/dev/doc/gfx/ozm-oz2.md

import io
import os
import sys
import struct
import numpy as np

try:
    from PIL import Image
except ImportError:
    pass  # This is handled inside functions that need it


# --- Palette Handling ---
class Palettes:
    def __init__(self, palette_file_path: str = "", order: str = "rgb"):
        if palette_file_path:
            self.palettes = self._load_palettes(palette_file_path, order)

    def color(self, index: int):
        return self.palettes[0][index]

    def set_palettes(self, data: bytearray, order: str = "rgb"):
        if len(data) % 48 != 0:
            raise ValueError(f"Invalid palette file size ({len(data)} bytes). Must be a multiple of 48.")
        self.palette = []
        for pos in range(16):
            color_data = data[pos * 3 : pos * 3 + 3]
            if len(color_data) < 3:
                break
            components = {"r": 0, "g": 0, "b": 0}
            for i, component_char in enumerate(order):
                if component_char in components:
                    components[component_char] = color_data[i]
            final_r = components["r"] * 17
            final_g = components["g"] * 17
            final_b = components["b"] * 17
            self.palette.append((final_r, final_g, final_b))

    def _load_palettes(self, palette_file_path, order="rgb"):
        palettes = []
        try:
            if not os.path.exists(palette_file_path):
                raise FileNotFoundError(f"File not found: {palette_file_path}")

            file_size = os.path.getsize(palette_file_path)
            if file_size % 48 != 0:
                raise ValueError(f"Invalid palette file size ({file_size} bytes). Must be a multiple of 48.")
            num_palettes = file_size // 48

            with open(palette_file_path, "rb") as f:
                for _ in range(num_palettes):
                    palette = []
                    for _ in range(16):
                        color_data = f.read(3)
                        if len(color_data) < 3:
                            break
                        components = {"r": 0, "g": 0, "b": 0}
                        for i, component_char in enumerate(order):
                            if component_char in components:
                                components[component_char] = color_data[i]
                        final_r = components["r"] * 17
                        final_g = components["g"] * 17
                        final_b = components["b"] * 17
                        palette.append((final_r, final_g, final_b))
                    palettes.append(palette)
        except (FileNotFoundError, IOError, IndexError) as e:
            print(f"Error reading palette file: {e}")
            return None
        return palettes


class OZM:
    def __init__(self):
        # Header information
        self.ver = 0
        self.palette_type = 0
        self.width_bytes = 0
        self.height = 0
        self.start_ofs = 0
        self.pixel_width = 0

        # Palette information
        self.raw_palette = bytearray()
        self.palette = Palettes()

        # Main data
        self.compressed_data = bytearray()
        self.planar_data = bytearray()
        self.data_8bpp = bytearray()

    def read_ozm(self, ozm_file_path):
        """
        Reads an OZM file, decompresses it, and returns the raw pixel data and dimensions.
        """
        with open(ozm_file_path, "rb") as f:
            # Read header
            self.ver = struct.unpack(">H", f.read(2))[0]  # Read 2 bytes
            if self.ver == 0x301:
                self.palette_type = 0x1

            self.width_bytes, self.height, self.start_ofs = struct.unpack("<HHH", f.read(6))
            self.pixel_width = self.width_bytes * 8

            if self.start_ofs == 0x3A:
                temp = f.read(1)
                if temp[0] != self.palette_type:
                    raise ValueError(
                        "Invalid OZM file: Expected palette type 0x{:02X}, got 0x{:02X}".format(
                            self.palette_type, temp[0]
                        )
                    )
            print(
                f"  Version: {self.ver:04X}, Size: {self.pixel_width}x{self.height}, Data offset: {self.start_ofs:04X}"
            )
            if self.ver not in [0x200, 0x300, 0x301]:
                print(f"  Warning: Unexpected version {self.ver:04X}", file=sys.stderr)

            if self.start_ofs in [0x39, 0x3A]:
                self.raw_palette = f.read(48)
                self.palette.set_palettes(self.raw_palette, order="rgb")

            f.seek(self.start_ofs)
            self.compressed_data = f.read()

    def decompress(self):
        if len(self.compressed_data) == 0:
            raise ValueError("Compressed data is empty.")

        self.planar_data = ozm_unpack_rle(self.compressed_data)
        print(f"  Decompressed {len(self.compressed_data)} bytes into {len(self.planar_data)} bytes of planar data.")
        # Generate 8bpp indexed data for comparison
        self.data_8bpp = convert_planar_to_8bpp_indexed(self.planar_data, self.width_bytes, self.height)

    def save_as_16color_png(self, output_path):
        if len(self.data_8bpp) == 0:
            raise ValueError("8bpp data is empty.")

        image_array = np.frombuffer(self.data_8bpp, dtype=np.uint8).reshape((self.height, self.pixel_width))
        img = Image.fromarray(image_array, mode="P")

        try:
            flat_palette = [value for color in self.palette.palette for value in color]
        except TypeError:
            print("Error: Failed to flatten palette data.")
            print("Please double-check the structure of the palette_16_colors variable.")
            sys.exit(1)

        # --- Debugging Check ---
        # Check if the first element of the converted palette is a tuple. If it is, this is the cause of the error.
        if flat_palette and isinstance(flat_palette[0], tuple):
            print("Error: 'flat_palette' was incorrectly converted to a list of tuples.")
            print("This is the cause of the TypeError. Please check the nested structure of 'palette_16_colors'.")
            print(f"First element of the incorrectly converted palette: {flat_palette[0]}")
            sys.exit(1)
        img.putpalette(flat_palette)
        img.save(output_path, "PNG")

    def save_as_png(self, out_path):
        # Convert 8bpp indexed data to RGB
        if len(self.data_8bpp) == 0:
            raise ValueError("8bpp data is empty.")

        rgb_pixels = []
        for index in self.data_8bpp:
            rgb_pixels.append(self.palette.palette[index])

        # Create new RGB Image
        rgb_img = Image.new("RGB", (self.pixel_width, self.height))
        rgb_img.putdata(rgb_pixels)

        rgb_img.save(out_path, "PNG")
        print(f"  Successfully saved True-Color image to {out_path}")

    def read_png_as_8bpp(self, png_path):
        img = Image.open(png_path).convert("RGB")
        width, height = img.size
        pixels = list(img.getdata())

        unpacked_pixels_8bpp = bytearray(width * height)
        for i, pixel_rgb in enumerate(pixels):
            unpacked_pixels_8bpp[i] = find_closest_color_index(pixel_rgb, self.palette.palette, "last")

        self.data_8bpp = unpacked_pixels_8bpp

    def compress(self, out_path):
        w = self.pixel_width >> 3
        h = self.height

        header = [
            3,
            self.palette_type,
            w & 255,
            w >> 8,
            h & 255,
            h >> 8,
            0x3A,
            0,
            self.palette_type,
        ]
        outbuf = bytearray(header)
        outbuf += bytearray(self.raw_palette)
        outbuf.append(0x0F)

        # The bitmap is an array of individual 4/8 bpp pixel values in scanline order.
        bitmap = self.data_8bpp
        bitmask = 1
        for i in range(4):
            # Process one bitplane at a time, first 0x01 the lowest bits.
            plane = bytearray(map(lambda x: (x & bitmask) >> i, bitmap))
            bitmask = bitmask << 1
            # Pack the plane into an 8px column.
            buf = bytearray()
            for x in range(w):
                ofs = x << 3
                for y in range(h):
                    row = 0
                    for j in range(8):
                        row += plane[ofs + j] << (7 - j)
                    buf.append(row)
                    ofs += self.pixel_width
            # RLE-compress the columnified bitplane, add to output buffer.
            y = 0
            while y < len(buf):
                if (y + 4 < len(buf)) and (buf[y] == buf[y + 1]) and (buf[y] == buf[y + 2]) and (buf[y] == buf[y + 3]):
                    outbuf.append(0)  # special code
                    outbuf.append(6)  # repeat next byte
                    i = buf[y]
                    outbuf.append(i)
                    rep = 4
                    y += 4
                    while (y < len(buf)) and (buf[y] == i):
                        rep += 1
                        y += 1
                    y -= 1
                    outbuf.append(rep & 255)
                    outbuf.append(rep >> 8)
                elif buf[y] != 0:
                    outbuf.append(buf[y])  # output literal
                else:
                    outbuf.append(0)  # special code
                    outbuf.append(1)  # one 0 byte
                y += 1

        with open(out_path, "wb") as f:
            f.write(outbuf)


# --- PNG to 8bpp indexed conversion (for True-Color PNGs) ---
def find_closest_color_index(rgb: tuple, palette: list, tie_breaking_rule: str = "first") -> int:
    """
    Finds the index of the closest color in the palette using Euclidean distance.
    tie_breaking_rule controls which index is chosen if multiple colors have the
    same minimal distance (e.g., duplicate colors in palette).
    'first': (default) chooses the first index found.
    'last': chooses the last index found.
    """
    r, g, b = rgb
    min_dist_sq = float("inf")
    best_index = 0

    if tie_breaking_rule == "first":
        for i, (pr, pg, pb) in enumerate(palette):
            dist_sq = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_index = i
            if dist_sq == 0:  # Exact match, short-circuit
                return best_index
    elif tie_breaking_rule == "last":
        for i, (pr, pg, pb) in enumerate(palette):
            dist_sq = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            if dist_sq <= min_dist_sq:  # Update on less than or *equal* to
                min_dist_sq = dist_sq
                best_index = i
            if dist_sq == 0:  # Exact match, continue to find last duplicate
                pass
    else:
        raise ValueError(f"Unknown tie_breaking_rule: '{tie_breaking_rule}'")

    return best_index


def convert_png_to_8bpp_indexed(
    png_path: str, palette_colors: list, tie_breaking: str = "first"
) -> tuple[bytearray, int, int]:
    """
    Converts a True-Color (RGB/RGBA) PNG to 8bpp indexed data by quantizing
    it against the provided palette, with a configurable tie-breaking rule.
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("Pillow library not found. Please install it with 'pip install Pillow'")

    print(f"Loading True-Color PNG '{png_path}' and quantizing to palette (tie-breaking: '{tie_breaking}')...")
    img = Image.open(png_path).convert("RGB")
    width, height = img.size
    pixels = list(img.getdata())

    unpacked_pixels_8bpp = bytearray(width * height)
    for i, pixel_rgb in enumerate(pixels):
        unpacked_pixels_8bpp[i] = find_closest_color_index(pixel_rgb, palette_colors, tie_breaking)

    print(
        "Quantization to 8bpp indexed format complete (Note: may not be byte-perfect to original game data if input colors differ)."
    )
    return unpacked_pixels_8bpp, width, height


# --- OZM RLE Decompression ---
def ozm_unpack_rle(data: bytes) -> bytearray:
    src = io.BytesIO(data)
    dest = bytearray()
    while True:
        cmd_byte = src.read(1)
        if not cmd_byte:
            break
        cmd = cmd_byte[0]
        if cmd != 0:
            dest.append(cmd)
        else:
            cmd_code_byte = src.read(1)
            if not cmd_code_byte:
                break
            cmd_code = cmd_code_byte[0]
            if 1 <= cmd_code <= 5:
                dest.extend([0] * cmd_code)
            elif cmd_code == 6:
                b = src.read(1)[0]
                reps = struct.unpack("<H", src.read(2))[0]
                dest.extend([b] * reps)
            elif cmd_code == 7:
                w_bytes = src.read(2)
                reps = struct.unpack("<H", src.read(2))[0]
                for _ in range(reps // 2):
                    dest.extend(w_bytes)
                if reps % 2 != 0:
                    dest.append(w_bytes[0])
    return dest


# --- Planar/Chunky/Bit-depth Conversions ---
def convert_planar_to_8bpp_indexed(planar_data: bytearray, width_bytes: int, height: int) -> bytearray:
    pixel_width = width_bytes * 8
    plane_size = width_bytes * height
    if len(planar_data) < 4 * plane_size:
        raise ValueError("Planar data is smaller than expected.")
    planes = [planar_data[i * plane_size : (i + 1) * plane_size] for i in range(4)]
    unpacked_pixels_8bpp = bytearray(pixel_width * height)
    for y in range(height):
        for x_byte in range(width_bytes):
            b0, b1, b2, b3 = [planes[p][x_byte * height + y] for p in range(4)]
            for bit_idx in range(8):
                bit = 7 - bit_idx
                p0 = (b0 >> bit) & 1
                p1 = (b1 >> bit) & 1
                p2 = (b2 >> bit) & 1
                p3 = (b3 >> bit) & 1
                color_index = (p3 << 3) | (p2 << 2) | (p1 << 1) | p0
                unpacked_pixels_8bpp[y * pixel_width + (x_byte * 8 + bit_idx)] = color_index
    return unpacked_pixels_8bpp


def convert_planar_to_packed_4bpp(planar_data: bytearray, width_bytes: int, height: int) -> bytearray:
    pixel_width = width_bytes * 8
    unpacked_pixels_8bpp = convert_planar_to_8bpp_indexed(planar_data, width_bytes, height)
    return pack_8bpp_to_4bpp(unpacked_pixels_8bpp, pixel_width, height)


def unpack_4bpp_to_8bpp(raw_4bpp_data: bytearray, width: int, height: int) -> bytearray:
    if len(raw_4bpp_data) != (width * height) // 2:
        raise ValueError("4bpp data length is incorrect.")
    unpacked_pixels_8bpp = bytearray(width * height)
    for i, byte in enumerate(raw_4bpp_data):
        unpacked_pixels_8bpp[i * 2] = byte >> 4
        unpacked_pixels_8bpp[i * 2 + 1] = byte & 0x0F
    return unpacked_pixels_8bpp


def pack_8bpp_to_4bpp(unpacked_pixels_8bpp: bytearray, width: int, height: int) -> bytearray:
    output_pixels_4bpp = bytearray(width * height // 2)
    for i in range(len(unpacked_pixels_8bpp) // 2):
        idx1 = unpacked_pixels_8bpp[i * 2]
        idx2 = unpacked_pixels_8bpp[i * 2 + 1]
        output_pixels_4bpp[i] = (idx1 << 4) | idx2
    return output_pixels_4bpp


def convert_chunky_8bpp_to_planar(unpacked_pixels_8bpp: bytearray, width: int, height: int) -> bytearray:
    width_bytes = width // 8
    planes = [bytearray() for _ in range(4)]
    for x_byte in range(width_bytes):
        for y in range(height):
            b = [0, 0, 0, 0]
            for bit_idx in range(8):
                pixel_x = x_byte * 8 + bit_idx
                color_index = unpacked_pixels_8bpp[y * width + pixel_x]
                p0, p1, p2, p3 = [(color_index >> i) & 1 for i in range(4)]
                bit = 7 - bit_idx
                b[0] |= p0 << bit
                b[1] |= p1 << bit
                b[2] |= p2 << bit
                b[3] |= p3 << bit
            for i in range(4):
                planes[i].append(b[i])
    return planes[0] + planes[1] + planes[2] + planes[3]


# --- OZM RLE Compression ---
def ozm_pack_rle(planar_data: bytearray) -> bytearray:
    """
    Compresses planar data using the OZM RLE-like algorithm, supporting all opcodes.
    It attempts to find the most efficient encoding for runs.
    """
    dest = bytearray()
    i = 0
    while i < len(planar_data):
        # Prioritize word runs (0x00, 0x07) - most efficient
        # Check for runs of 2-byte sequences
        if i + 3 < len(planar_data) and planar_data[i : i + 2] == planar_data[i + 2 : i + 4]:
            w_bytes = planar_data[i : i + 2]
            count = 0
            while i + count + 1 < len(planar_data) and planar_data[i + count : i + count + 2] == w_bytes:
                count += 2

            if count >= 4:  # Only if it's a run of at least 2 words (4 bytes)
                dest.extend([0, 7])
                dest.extend(w_bytes)
                dest.extend(struct.pack("<H", count))
                i += count
                continue

        # Next, prioritize byte runs (0x00, 0x06) - 4+ identical bytes
        if (
            i + 3 < len(planar_data)
            and planar_data[i] == planar_data[i + 1]
            and planar_data[i] == planar_data[i + 2]
            and planar_data[i] == planar_data[i + 3]
        ):
            run_byte = planar_data[i]
            count = 0
            while i + count < len(planar_data) and planar_data[i + count] == run_byte and count < 65535:
                count += 1

            dest.extend([0, 6])
            dest.append(run_byte)
            dest.extend(struct.pack("<H", count))
            i += count
            continue

        # Next, handle zero runs (0x00, 0x01 to 0x00, 0x05)
        if planar_data[i] == 0:
            count = 0
            while i + count < len(planar_data) and planar_data[i + count] == 0 and count < 5:
                count += 1

            if count > 0:
                dest.extend([0, count])
                i += count
                continue

        # Finally, a literal non-zero byte
        if planar_data[i] != 0:
            dest.append(planar_data[i])
            i += 1
            continue

        # If we reach here, it's a single zero not caught by the zero-run logic
        # This shouldn't happen with the current order, but as a safeguard.
        dest.extend([0, 1])  # Explicitly encode a single 0 if somehow missed
        i += 1

    return dest
