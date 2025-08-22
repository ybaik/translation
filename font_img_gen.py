import numpy as np
from PIL import Image


def save_font_image(
    font_path,
    font_width,
    font_height,
    im_cols,
    im_rows,
    font_img_path,
    use_little_endian=False,
    offset=0,
    draw_vertical=False,
):
    if font_width == 8:
        bitchk = 7
    elif font_width == 16:
        font_width == 16
        bitchk = 15
    else:
        assert 0, f"font_width should be 8 or 16, but {font_width} is given."

    with open(font_path, "rb") as f:
        data = np.frombuffer(f.read(), dtype=np.uint8)

    image_width, image_height = im_cols * font_width, im_rows * font_height + offset
    end = image_width * image_height + offset
    end = max(len(data), end)
    data = data[offset : end + 1]

    if font_width == 16:
        data = np.frombuffer(data.tobytes(), dtype=np.uint16)

    max_len = len(data)
    current_len = 0

    if use_little_endian:  # For Little Endian
        data = data.byteswap()

    # initialize the buffer with 255 (white)
    image_buffer = np.full((image_height, image_width), 255, dtype=np.uint8)

    for idx in range(im_rows * im_cols):
        if max_len <= current_len:
            break

        if draw_vertical:
            x = (idx // im_rows) * font_width
            y = (idx % im_rows) * font_height
        else:
            x = (idx % im_cols) * font_width
            y = (idx // im_cols) * font_height

        font_data = data[idx * font_height : (idx + 1) * font_height]

        for r in range(font_height):
            for c in range(font_width):
                if font_data[r] & (1 << (bitchk - c)):
                    image_buffer[y + r, x + c] = 0

        current_len += font_height

    print(max_len, current_len)
    image = Image.fromarray(image_buffer, mode="L")
    image.save(font_img_path)


def main():
    # # Read 8x16 font
    font_path = r"C:\Users\hyunx\Downloads\genpei_200608\genpei\jis.fnt"
    font_width, font_height = 8, 16
    im_cols, im_rows = 16, 14
    font_img_path = "C:/work_han/workspace/font_chr.png"
    save_font_image(
        font_path=font_path,
        font_width=font_width,
        font_height=font_height,
        im_cols=im_cols,
        im_rows=im_rows,
        font_img_path=font_img_path,
        use_little_endian=False,
        draw_vertical=False,
    )

    offset = im_cols * font_width * im_rows * font_height
    # Read 16x16 font
    font_path = r"C:\Users\hyunx\Downloads\genpei_200608\genpei\jis.fnt"
    font_width, font_height = 16, 16
    offset = 0
    im_cols, im_rows = 70, 64
    font_img_path = "C:/work_han/workspace/han_fnt.png"
    save_font_image(
        font_path=font_path,
        font_width=font_width,
        font_height=font_height,
        im_cols=im_cols,
        im_rows=im_rows,
        font_img_path=font_img_path,
        use_little_endian=True,
        offset=offset,
        draw_vertical=False,
    )


if __name__ == "__main__":
    main()
