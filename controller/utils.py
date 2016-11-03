
def str_to_rgb_tuple(string):
    if len(string) == 7:
        string = string[1:]  # removes the hash symbol
        rgb_list = [int(string[i:i + 2], 16) for i in range(0, len(string), 2)]
        return tuple(rgb_list)
    else:
        raise AttributeError("Invalid Colour length " + str(len(string)))


def rgb_tuple_to_string(colour_tuple):
    if len(colour_tuple) == 3:
        for c in colour_tuple:
            assert 0 <= c <= 255
        return '#%02x%02x%02x' % tuple(colour_tuple)
    else:
        raise AttributeError("Invalid Tuple: "+str(colour_tuple))

def tuple_to_scalar(values):
    return [v/255.0 for v in values]




if __name__ == '__main__':
    print str_to_rgb_tuple("#121212")
    print rgb_tuple_to_string([0, 255, 254])
    print tuple_to_scalar([128,10,54])
