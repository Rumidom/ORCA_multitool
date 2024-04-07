def ASCII_Decode(b_arr):
    return bytearray((x if x <= 127 else ord('?') for x in b_arr))
