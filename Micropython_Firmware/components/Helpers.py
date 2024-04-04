def ASCII_Decode(byte_array):
    result = ""
    for byte in byte_array:
        if 0 <= byte <= 127:
            result += chr(byte)
        else:
            result += "?"
    return result