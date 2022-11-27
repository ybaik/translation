import os
from time import time
from typing import Optional, Tuple


class LZSS_DS:  # for dark seraphim (pc98, dos)
    def __init__(self):
        self.head_size = 6
        self.window_size = int("0xf", 16) + 4
        self.max_match_section = int("0xfff", 16)
        self.code_offset = 3

    def _get_wrapped_slice(self, x: bytes, num_bytes: int) -> bytes:
        """
        Examples:
            f(b"1234567", 5) -> b"12345"
            f(b"123", 5) -> b"12312"
        """
        repetitions = num_bytes // len(x)
        remainder = num_bytes % len(x)
        return x * repetitions + x[:remainder]

    def _find_longest_match(
        self, data: bytearray, current_position: int
    ) -> Optional[Tuple[int, int]]:
        end_of_buffer = min(current_position + self.window_size, len(data))
        search_start = max(0, current_position - self.max_match_section)
        for target_end in range(end_of_buffer, current_position + self.code_offset, -1):
            target = data[current_position:target_end]
            target_length = len(target)
            # print(target_length, hex(target[0]), hex(target[-1]))
            # print([hex(t) for t in target])

            for search_position in range(
                search_start, current_position - target_length + 1
            ):
                candidate = data[search_position : search_position + target_length]
                # print(len(candidate), hex(candidate[0]), hex(candidate[-1]),search_position, search_position+target_length)

                if target_length != len(candidate):
                    print(target_length, hex(target[0]), hex(target[-1]))
                    print(
                        len(candidate),
                        hex(candidate[0]),
                        hex(candidate[-1]),
                        search_position,
                        search_position + target_length,
                    )
                    print(1)
                # val = self._get_wrapped_slice(data[search_position:current_position], len(match_candidate))
                # if target == self._get_wrapped_slice(data[search_position:current_position], len(match_candidate)):
                #
                if target == candidate:
                    return current_position - search_position, len(candidate)

    def compress(self, original_data: bytearray):
        # check header
        if original_data[0] != 5 or original_data[1] != 0:
            print("Wrong data format...")
            return bytearray()

        output_buffer = bytearray()

        # file info
        compression_code = original_data[2]
        data_size = original_data[4] + (original_data[5] << 8)
        file_size = self.head_size + data_size
        print(f"Original file size: {file_size:,} bytes")
        print(f"compression code: {hex(compression_code)}")

        # append header
        output_buffer += original_data[: self.head_size]

        # compression
        i = self.head_size
        while i < file_size:
            # if i < 6592:
            #     i += 1
            #     continue
            if len(output_buffer) >= int("1533", 16):
                print(i)
                print(1)
            if match := self._find_longest_match(original_data, i):
                match_distance, match_length = match
                output_buffer.append(compression_code)
                output_buffer.append(match_distance & 0xFF)
                output_buffer.append(((match_length - 4) << 4) + (match_distance >> 8))
                i += match_length
            else:
                output_buffer.append(original_data[i])
                i += 1
        return output_buffer

    def decompress(self, compressed_data: bytearray) -> bytearray:
        # check header
        if compressed_data[0] != 5 or compressed_data[1] != 0:
            print("Wrong data format...")
            return bytearray()

        output_buffer = bytearray()

        # file info
        compression_code = compressed_data[2]
        data_size = compressed_data[4] + (compressed_data[5] << 8)
        file_size = self.head_size + data_size
        compressed_size = len(compressed_data)
        print(f"Compressed file size: {compressed_size:,} bytes")
        print(f"Expected decompressed file size: {file_size:,} bytes")
        print(f"compression code: {hex(compression_code)}")

        # append header
        output_buffer += compressed_data[: self.head_size]

        i = self.head_size
        length_min = 1000
        length_max = -1
        prevpt_min = 1000
        prevpt_max = -1

        # decompression
        while i < compressed_size:

            if compressed_data[i] != compression_code:  # pattern
                output_buffer.append(compressed_data[i])
                i += 1
            else:
                # read compression info.
                # length: 4 bits, distance: 12 bits
                length = (compressed_data[i + 2] >> 4) + 4
                distance = compressed_data[i + 1] + (
                    (compressed_data[i + 2] & 0xF) << 8
                )

                length_min = min(length_min, length)
                length_max = max(length_max, length)
                prevpt_min = min(prevpt_min, distance)
                prevpt_max = max(prevpt_max, distance)

                # log = f"{idx:02x}:{compressed_data[idx]:02x}-{compressed_data[idx+1]:02x}-{compressed_data[idx+2]:02x}"
                # print(log)

                # read previous data
                target_mem_pos = len(output_buffer) - distance
                output_buffer += output_buffer[target_mem_pos : target_mem_pos + length]
                i += 3

        # print(length_min, length_max)
        # print(prevpt_min, prevpt_max)
        return output_buffer


def main():

    # decompress
    data_path = "D:/work_han/workspace/kor/OPEN_encoded.ASS"
    decoded_path = "D:/work_han/workspace/kor/OPEN_decoded.ASS"
    save_path = "D:/work_han/workspace/kor/OPEN.ASS"

    lzss_ds = LZSS_DS()
    # decode
    # read the compressed file
    if not os.path.exists(data_path):
        return

    with open(data_path, "rb") as f:
        compressed_data = f.read()
    compressed_data = bytearray(compressed_data)
    print(f"Data size: {data_path}({len(compressed_data):,} bytes)")

    decompressed_data = lzss_ds.decompress(compressed_data)
    with open(decoded_path, "wb") as f:
        f.write(decompressed_data)
    return

    # encode
    with open(decoded_path, "rb") as f:
        decompressed_data = f.read()
    decompressed_data = bytearray(decompressed_data)
    print(f"Data size: {decoded_path}({len(decompressed_data):,} bytes)")

    # compress
    start = time()
    compressed_data_ = lzss_ds.compress(decompressed_data)
    end = time()
    print(f"{end-start:.5f} sec")
    with open(save_path, "wb") as f:
        f.write(compressed_data_)


if __name__ == "__main__":
    main()
