

def extract_scripts(data, font_table, length_threshold):

    i=0
    length = 0 # sentence length
    sentence = ''
    sentence_log = ''
    script = dict()
    script_log = dict()

    while i < len(data)-1:
        # extract a 2byte code
        code_int = (data[i]<<8) + data[i+1]
        code_hex = hex(code_int)

        # check if value is in range of the source font table
        if font_table.range(code_int):
            # find a character in the font table
            character = font_table.get_char(code_hex)

            if character: # character is in the font table
                sentence += character
                if character == '■': 
                    sentence_log += f':{code_hex}' if sentence_log else f'{code_hex}'
                length += 1
                i += 1
            else: # character is not in the font table
                sentence += '@'
                sentence_log += f':@{code_hex}' if sentence_log else f'@{code_hex}'
                length += 1
                i += 1
        else:
            # check sentence length and save
            if length >= length_threshold:
                address = f'{hex(i-length*2)}={hex(i-1)}'
                script[address] = sentence
                if sentence_log:
                    script_log[address] = sentence_log
            sentence = ''
            sentence_log = ''
            length = 0
        i += 1

    # check a result of the end of data
    if length >= length_threshold:
        address = f'{hex(i-length*2)}={hex(i-1)}'
        script[address] = sentence
        if sentence_log:
            script_log[address] = sentence_log
        sentence = ''
        sentence_log = ''
        length = 0

    return script, script_log


def write_scripts(data, font_table, scripts):

    # write scripts
    for range, sentence in scripts.items():
        [code_hex_start, code_hex_end] = range.split('=')
        spos = int(code_hex_start, 16) 
        epos = int(code_hex_end, 16)
        pos = spos
        # write letters in the sentence
        for i, letter in enumerate(sentence):
            if font_table.get_code(letter) is not None:
                code_hex = font_table.get_code(letter)
                code_int = int(code_hex, 16)

                code1 = (code_int & 0xff00) >> 8
                code2 = (code_int & 0x00ff)
                data[pos] = code1
                data[pos+1] = code2
            else:
                assert 0, f'{letter} is not in the font table.'
            pos += 2

    return data