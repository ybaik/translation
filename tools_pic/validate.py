import sys
import os

DEBUG = False # Changed to False


def compare_binary_files(file1_path: str, file2_path: str) -> None:
    """
    Compares two binary files byte by byte and reports differences.
    """
    print(f"Comparing '{file1_path}' and '{file2_path}'...")

    if not os.path.exists(file1_path):
        print(f"Error: File not found: {file1_path}", file=sys.stderr)
        return
    if not os.path.exists(file2_path):
        print(f"Error: File not found: {file2_path}", file=sys.stderr)
        return

    try:
        with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
            content1 = f1.read()
            content2 = f2.read()

        if content1 == content2:
            print("SUCCESS: Files are identical.")
            return

        print("FAILURE: Files are NOT identical.")

        if len(content1) != len(content2):
            print(
                f"  - Length mismatch: '{file1_path}' has {len(content1)} bytes, "
                f"'{file2_path}' has {len(content2)} bytes."
            )

        # Find first differing byte
        min_len = min(len(content1), len(content2))
        for i in range(min_len):
            if content1[i] != content2[i]:
                print(f"  - First difference at offset 0x{i:X} ({i} decimal):")
                print(f"    - '{file1_path}': 0x{content1[i]:02X}")
                print(f"    - '{file2_path}': 0x{content2[i]:02X}")
                return

        # This case is reached if lengths differ but common prefix is identical
        if len(content1) > len(content2):
            print(
                f"  - Files are identical up to {min_len} bytes. '{file1_path}' is longer."
            )
        else:  # len(content2) > len(content1)
            print(
                f"  - Files are identical up to {min_len} bytes. '{file2_path}' is longer."
            )

    except IOError as e:
        print(f"Error reading files: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    if not DEBUG:
        if len(sys.argv) != 3:
            print(
                "Usage: python validate.py <file1_path> <file2_path>", file=sys.stderr
            )
            sys.exit(1)

        file1 = sys.argv[1]
        file2 = sys.argv[2]
    else:
        # Debug mode for comparing 8bpp raw files (e.g. "TITLE0.8bpp.raw" vs "TITLE0_comp.8bpp.raw")
        file1 = "TITLE0.8bpp.raw"
        file2 = "TITLE0_comp.8bpp.raw"

    compare_binary_files(file1, file2)