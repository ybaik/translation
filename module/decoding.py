def decode(data, encoding_info):
    if "xor" in encoding_info:
        encoding_key = encoding_info.split(":")[-1]
        encoding_key = int(encoding_key, 16)
        data = bytearray([b ^ encoding_key for b in data])
    return data


def encode(data, encoding_info):
    if "xor" in encoding_info:
        encoding_key = encoding_info.split(":")[-1]
        encoding_key = int(encoding_key, 16)
        data = bytearray([b ^ encoding_key for b in data])
    return data
