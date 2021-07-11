
def main():

    bin_src_path = '../workspace/DS_final/MAIN.EXE'
    bin_dst_path = '../workspace/DS_final/MAIN_old.EXE'

    with open(bin_src_path, 'rb') as f: 
        data_src = f.read()
    with open(bin_dst_path, 'rb') as f: 
        data_dst = f.read()

    if len(data_src) != len(data_dst):
        print('Data sizes are different.')
        return

    for i in range(len(data_src)):
        if data_src[i] != data_dst[i]:
            print(hex(i))


if __name__ == "__main__":
    main()




