from module.name_db import NameDB


def main():
    errors = NameDB().validate()
    for error in errors:
        print(error)
    print(f"Number of errors = {len(errors)}")


if __name__ == "__main__":
    main()
