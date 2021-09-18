import os
import pandas as pd


filter = ['.', '!', '?', '_', '\n'] 

table_cho = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ','ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
table_jung = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
table_jong = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 
              'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']


def unicode2chohap(code_int):
    base_int = int('0xac00', 16)
    cho = (((code_int - base_int) // 28) // 21) % 19
    jung = ((code_int - base_int) // 28) % 21
    jong = (code_int - base_int) % 28
    return cho, jung, jong

def chohap2unicode(cho, jung, jong):
    base_int = int('0xac00', 16)
    code_int = base_int + 28*21*cho + 28*jung + jong
    return chr(code_int)


def main():
    
    base_path = '../Han/마크로스작업/S1'
    path_list = os.listdir(base_path)

    # read tbl
    '''
    with open('../Han/마크로스작업/data/macross.tbl', 'r') as f:
        lines = f.readlines()

    table = dict()
    letters = []
    for line in lines:
        line = line.rstrip()
        a = line.split('=')
        letters.append(a[-1])
        table[a[1]] = a[0]

    letters = list(table.keys())
    '''
    #'''
    df = pd.read_csv('../Han/마크로스작업/data/macross-dos-table.csv', encoding='utf-8-sig')
    print(df)

    table_new = ''
    for cho_idx in range(len(table_cho)):
        for jung_idx in range(len(table_jung)):
            letter_base = chohap2unicode(cho_idx, jung_idx, 0)
            cho = table_cho[cho_idx]
            code_hex_base = df.at[jung_idx, cho]
            code_int_base = int(code_hex_base, 16)
            code_hex_base = code_hex_base.replace('0x', '').upper()
            table_new += f'{code_hex_base}={letter_base}\n' 

            for jong_idx in range(1, len(table_jong)):
                letter = chohap2unicode(cho_idx, jung_idx, jong_idx)
                if jong_idx >= 17:
                    jong_idx += 1
                code_int = code_int_base + jong_idx
                code_hex = hex(code_int).replace('0x', '').upper()
                table_new += f'{code_hex}={letter}\n' 
    with open('../Han/마크로스작업/data/macross-new.tbl', 'w') as f:
        f.write(table_new)
    #'''
       




    '''
    print(len(table_jung),len(table_cho))
    print(table_cho)
    df = pd.DataFrame(index=table_jung, columns= table_cho)
    for letter in letters:
        cho, jung, jong = unicode2chohap(ord(letter))
        if jong == 0:
            #print(letter, table[letter])
            code_int = int(table[letter], 16)

            letter_cho = table_cho[cho]
            letter_jung = table_jung[jung]

            df.at[letter_jung, letter_cho] = hex(code_int)
    
    df.to_csv('../test.csv', encoding="utf-8-sig")
    #'''




    '''
    letters = list(table.keys())
    for letter in letters:
        code_int = ord(letter)
        cho, jung, jong = unicode2chohap(code_int)
        print(table_cho[cho], table_jung[jung], table_jong[jong])


        base_letter = chohap2unicode(cho, jung, 0)
        code_int_base = int((table[base_letter]), 16)

        if jong >= 17:
            jong += 1
        code_int_target = code_int_base + jong
        
        code = '0x' + table[letter]
        code = code.lower()
        print(base_letter, letter, code, hex(code_int_target))        
        if code != hex(code_int_target):
            print('a')
    '''


    '''
    letters = list(table.keys())

    new_table = ''

    for letter in letters:
        code_int = ord(letter)
        cho, jung, jong = unicode2chohap(code_int)
        if jong:
            continue

        # base letter setting
        base_letter = chohap2unicode(cho, jung, 0)
        code_int_base = int((table[base_letter]), 16)
        code_hex_base = hex(code_int_base).replace('0x', '').upper()
        #new_table[code_hex_base] = base_letter
        new_table += f'{code_hex_base}={base_letter}\n'

        print(table_cho[cho], table_jung[jung], table_jong[jong])

        for i in range(1, len(table_jong)):
            letter_target = chohap2unicode(cho, jung, i)
            j = i + 1 if i >= 17 else i
            code_int_target = code_int_base + j
            code_hex_target = hex(code_int_target).replace('0x', '').upper()

            #if table.get(letter_target) is not None:
            #    aa = table.get(letter_target)

            #new_table[code_hex_target] = letter_target
            new_table += f'{code_hex_target}={letter_target}\n'

    with open('../Han/마크로스작업/data/macross-new.tbl', 'w') as f:
         f.write(new_table)
    '''

        

   


if __name__ == "__main__":
    main()