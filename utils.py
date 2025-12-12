import json
import os
from oklch import *
from parseSVG import *
import math





def change_svg_colour(filepath, new_colour, old_colour, save_to_dir = 'assets/coloured/', name=''):
    """
    Open an SVG file, change its colours, save it for later use
    :param filepath: string filename of input SVG file
    :param new_colour: the colour to be added
    :param old_colour: the colour to be replaced in favour of new_colour
    :return: none
    """
    with open(filepath, 'r') as f:
        s = f.read()

    found = False
    if type(old_colour) == str:
        old_options = [old_colour, old_colour.lower(), old_colour.upper()]
        for old in old_options:
            found = (old in s) or found
            s = s.replace(old, new_colour)
        if not found:
            print('Warning: no colour change to', filepath, old_colour)
    else:
        print('Warning: old colour was not string and hence not changed', filepath, old_colour)

    endpath = filepath.split('/')[-1]

    if not name.endswith(':'):
        name += ':'
    if not os.path.exists(save_to_dir):
        os.makedirs(save_to_dir)
    newpath =  save_to_dir + name + endpath
    with open(newpath, 'w') as g:
        print(s, file=g)
    return newpath


def oklch_to_hex(l, c, h):
    """
    Convert from OKlch to hex representation of sRGB. If colour doesn't
    exist in sRGB use the nearest approximation using approximate_valid_srgb_for_oklch.
    >>> oklch_to_hex(96.8211630743405/100, 0.2087535023088284, 109.73795453564486)
    '#ffff14'
    """
    if l > 1:
        print('Invalid input luminence', l)
        l /= 100 # whyyyyyyy

    # does Aditya's code avoid the need for this?
    adjusted = [l, c, h]#approximate_valid_srgb_for_oklch([l, c, h])
    '''
    except:
         adjusted = [l, 0, h] # TODO
         print('Problem with', l, c, h)
         #rgb = oklch2rgb([l, c, h])
    '''
    if adjusted[0] > 1:
        adjusted[0] /= 100 # wtf is this in the code
        print('Invalid luminence corrected', adjusted)

    rgb = oklch2rgb(adjusted)
    return rgb_to_hex(*rgb)

def rgb_to_hex(r,g,b):
    # https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string
    return "#{:02x}{:02x}{:02x}".format(r,g,b)







def add_implicit_segments(s):
    # TODO add these!!!
    if seg[0] == 'C' and seg.count(',') < 4:
        added_commas = seg.replace(' ', ',')
        refined_sections.append(added_commas)

    elif seg[0] == 'C' and seg.count(',') % 3 == 0:
        added_commas = seg.replace(' ', ',')
        coords = added_commas[1:].split(',')

        curves = ['C']
        for i, c in enumerate(coords):
            if i % 6 == 5 and i > 0:
                curves[-1] = curves[-1] + c + ''
                curves += ['C']
            else:
                curves[-1] = curves[-1] + c + ','

        for new_seg in curves:
            if len(new_seg) > 2:
                refined_sections.append(new_seg)
            else:
                print('WARNING', new_seg)



if __name__ == '__main__':
    doctest.testmod()