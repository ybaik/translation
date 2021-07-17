import os
import sys
sys.path.append('./')
from module.font_table import FontTable

def main():
    
    # read font table
    font_table = FontTable('font_table/anex86jpn-full.json')

    # code to letter
    #codes = ['0x88d7', '0x94ca']
    codes = ['88d7', '94ca']
    letter = font_table.get_char(codes[0])
    word = font_table.get_chars(codes)
    print(letter, word)

    # letter to code
    code_hex = font_table.get_code('_')    
    codes_hex = font_table.get_codes('__')    

    print(code_hex, codes_hex)



    

if __name__ == "__main__":
    main()