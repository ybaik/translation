import os

def main():

    src_path = '../workspace/m3_jpn'
    dst_path = '../workspace/m3_kor'


    flist = os.listdir(src_path)

    for fn in flist:
        #print(fn)
        #bin_src_path = '../workspace/DS_final/MAIN.EXE'
        #bin_dst_path = '../workspace/DS_final/MAIN_old.EXE'
        bin_src_path = f'{src_path}/{fn}'
        bin_dst_path = f'{dst_path}/{fn}'

        with open(bin_src_path, 'rb') as f: 
            data_src = f.read()
        with open(bin_dst_path, 'rb') as f: 
            data_dst = f.read()

        if len(data_src) != len(data_dst):
            print(f'{fn}: Data sizes are different.')
            continue
        
        #print(len(data_src))
        for i in range(len(data_src)):
            if data_src[i] != data_dst[i]:
                #print(hex(i))
                print(f'{fn}: Contents are different.')
                break


if __name__ == "__main__":
    main()




