from pyqrcode import QRCode
from PIL import Image
import numpy as np


def generate_qr_code(msg="Hello World", filename="qr.png", scale=6, version=40):
    url = QRCode(msg, version=version)
    url.png(filename, scale=6)


def get_qr_pixels(filename="qr.png"):
    img_file = Image.open(filename)
    img_file.show()
    width, height = img_file.size
    data = img_file.convert("L")
    data = list(data.getdata())

    img_pixels = []
    for i in range(0, height):
        img_pixels.append(data[(i * width):((i + 1) * width)])

    if((len(img_pixels) * len(img_pixels[0])) == len(data)):
        return img_pixels

    return []


def get_message():
    return str(input("Enter the message to Encode in the qr code: "))


def str_bin(msg):
    return "" . join(format(ord(char), "08b") for char in msg)


def bin_str(msg):
    size = int(len(msg) / 8)
    return "" . join(chr(int("0b" + msg[i * 8:(i + 1) * 8], 2)) for i in range(0, size))


def is_single_coloured(mp):
    color = mp[0]
    for i in mp:
        if i != color:
            return False
    return True


def change_cmp(cmp, bit):
    initial_color = cmp[0]
    pos = 0
    for i in range(len(cmp)):
        if cmp[i] != initial_color:
            pos = i - 1
            break

    if(bit == 1):
        cmp[pos + 1] = 254 if cmp[pos] == 255 else 1
    else:
        cmp[pos + 1] = 2 if cmp[pos] == 0 else 253

    return cmp


def match_adjustment(pmp, cmp):
    complementary = (pmp[0] != cmp[0])
    new_cmp = cmp[:]

    for i in range(8):
        if complementary:
            if pmp[i] == 255:
                new_cmp[i] = 0
            else:
                new_cmp[i] = 255
        else:
            new_cmp[i] = pmp[i]
    return new_cmp


def hide_msg(img_pixels, msg, k=1):
    # TODO:A Method To Check if we can Hide the Data inside msg or not
    pos = 0
    size = len(msg)

    rows = len(img_pixels)
    cols = len(img_pixels[0])

    pmp = None
    cmp = None

    for i in range(rows):
        for j in range(0, cols - 6, 8):
            cmp = [img_pixels[i][j + k] for k in range(8)]
            if(i > 1):
                pmp = [img_pixels[i - 1][j + k] for k in range(8)]
                if is_single_coloured(pmp):
                    if not is_single_coloured(cmp) and pos < size:
                        new_cmp = change_cmp(cmp[:], int(msg[pos]))
                        for k in range(8):
                            img_pixels[i][j + k] = new_cmp[k]
                        pos += 1
                else:
                    if not is_single_coloured(cmp):
                        new_cmp = match_adjustment(pmp, cmp)
                        for k in range(8):
                            img_pixels[i][j + k] = new_cmp[k]
                        continue
            else:
                if not is_single_coloured(cmp) and pos < size:
                    new_cmp = change_cmp(cmp[:], int(msg[pos]))
                    for k in range(8):
                        img_pixels[i][j + k] = new_cmp[k]
                    pos += 1

    return img_pixels


def get_msg_bit(cmp):
    if (1 in cmp) or (254 in cmp):
        return 1
    elif (2 in cmp) or (253 in cmp):
        return 0
    else:
        return None


def retrieve_msg(img_pixels, k=1):
    ret_string = ""
    pmp = None
    cmp = None
    rows = len(img_pixels)
    cols = len(img_pixels[0])

    for i in range(rows):
        for j in range(0, cols - 6, 8):
            cmp = [img_pixels[i][j + k] for k in range(8)]
            if i > 1:
                pmp = [img_pixels[i - 1][j + k] for k in range(8)]
                if not is_single_coloured(cmp):
                    if is_single_coloured(pmp):
                        bit = get_msg_bit(cmp)
                        if bit != None:
                            ret_string += str(bit)
            else:
                bit = get_msg_bit(cmp)
                if bit != None:
                    ret_string += str(bit)
    
    return ret_string


def convert_to_long_list(img_pixels):
    ret_list = []
    row = len(img_pixels)
    col = len(img_pixels[0])

    for i in range(row):
        for j in range(col):
            ret_list.append(img_pixels[i][j])

    return ret_list


def main():
    generate_qr_code(version=40, msg="Hello, How are you?")
    img_pixels = get_qr_pixels()

    msg = get_message()
    bin_msg = str_bin(msg)

    hide_msg(img_pixels, bin_msg)
    
    decoded_msg = retrieve_msg(img_pixels)
    decoded_msg = bin_str(decoded_msg)

    width = len(img_pixels)
    height = len(img_pixels[0])

    img_pixels = convert_to_long_list(img_pixels)
    img_arr = np.array(img_pixels, np.uint8)
    img_arr = np.reshape(img_arr, (width, height))
    im = Image.fromarray(img_arr)

    im.show()


if __name__ == "__main__":
    main()
