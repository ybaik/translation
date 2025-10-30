def _xor_process(data, encoding_info):
    if "xor" in encoding_info:
        encoding_key = encoding_info.split(":")[-1]
        encoding_key = int(encoding_key, 16)
        data = bytearray([b ^ encoding_key for b in data])
    return data


def decode(data, encoding_info):
    return _xor_process(data, encoding_info)


def encode(data, encoding_info):
    return _xor_process(data, encoding_info)


def convert_3to4bpp(in_path, out_path):
    with open(in_path, "rb") as f_in, open(out_path, "wb") as f_out:
        while chunk := f_in.read(3):
            f_out.write(chunk)
            if len(chunk) == 3:
                f_out.write(b"\x00")


def convert_4to3bpp(in_path, out_path):
    with open(in_path, "rb") as f_in, open(out_path, "wb") as f_out:
        while True:
            chunk = f_in.read(4)
            if len(chunk) < 4:
                f_out.write(chunk[:3])
                break
            f_out.write(chunk[:3])
