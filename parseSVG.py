import doctest
import drawsvg as draw
from bs4 import BeautifulSoup
import sys

# we use this information to figure out commas
SEG_COORDS = {'M':2, 'S':4, 'L':2, 'Z':0, 'C':6, 'Q':4, 'A':7, 'V':1, 'H':1 }


def remove_svg_path_whitespace(s, seg_types=('M', 'S', 'L', 'Z', 'C', 'Q', 'A', 'H', 'V') ):
    """

    :param s:
    :param seg_types:
    :return:
    >>> remove_svg_path_whitespace('M 106.14893,154.92896 105.12057,156.28805 ')
    'M106.14893,154.92896 105.12057,156.28805'
    >>> remove_svg_path_whitespace('M 40.071 0.082 C 37.81 0.104 35.561 0.192 33.359 0.344 L 33.359 23.126 C 35.561 23.278 37.812 23.365 40.071 23.387 Z')
    'M40.071 0.082 C37.81 0.104 35.561 0.192 33.359 0.344 L33.359 23.126 C35.561 23.278 37.812 23.365 40.071 23.387 Z'
    >>> remove_svg_path_whitespace('L 0 30.11 C 0 30.821 0.579 31.4 1.29 31.4 L 8.758 31.4 L 8.789 31.4 L 14.271 31.4 C 14.983 31.399 15.561 30.821 15.561 30.11 Z')
    'L0 30.11 C0 30.821 0.579 31.4 1.29 31.4 L8.758 31.4 L8.789 31.4 L14.271 31.4 C14.983 31.399 15.561 30.821 15.561 30.11 Z'
    """
    for t in seg_types:
        s = s.replace(t + ' ', t)
    #assert not ' ' in s[:5], s
    return s.rstrip()


def separate_svg_path(s):
    """
    Take a string representing an SVG path and turn it into a new string that
    represents the path. TODO: implicit C/L/H/etc
    :param s: a path string. Must be all absolute.
    :return:
    >>> s = 'M233.14606,2008.031C659.81265,2747.0389999999998,1783.8721,2105.1105,1357.2055,1366.1024C1781.7582,619.3380099999999,2919.4029,1263.3265999999999,2484.9812,2004.3931M1366.1206,76.818124C507.12735,71.109224,498.21223,1371.7897,1357.2055,1366.1024M2637.1773000000003,1366.1184C2648.5952,-351.86798,65.859465,-351.90088,77.233765,1366.0864C88.458065,3061.4318,2625.91,3061.4641,2637.1773,1366.1184Z'
    >>> separate_svg_path(s)
    ['M233.14606,2008.031', 'C659.81265,2747.0389999999998,1783.8721,2105.1105,1357.2055,1366.1024', 'C1781.7582,619.3380099999999,2919.4029,1263.3265999999999,2484.9812,2004.3931', 'M1366.1206,76.818124', 'C507.12735,71.109224,498.21223,1371.7897,1357.2055,1366.1024', 'M2637.1773000000003,1366.1184', 'C2648.5952,-351.86798,65.859465,-351.90088,77.233765,1366.0864', 'C88.458065,3061.4318,2625.91,3061.4641,2637.1773,1366.1184', 'Z']
    >>> s = 'M 1366.1206,76.818124 C 507.12735,71.109224 498.21223,1371.7897 1357.2055,1366.1024'
    >>> separate_svg_path(s)
    ['M1366.1206,76.818124', 'C507.12735,71.109224,498.21223,1371.7897,1357.2055,1366.1024']
    >>> s = 'M 106.14893,154.92896 105.12057,156.28805' # implicit L
    >>> separate_svg_path(s)
    ['M106.14893,154.92896', 'L105.12057,156.28805']
    >>> s = 'M 115.52497,142.25383 C 115.44127,142.41816 115.3224,142.56184 115.1777,142.67553 L 114.49352,143.20985 114.16485,144.01395 C 114.08115,144.21859 113.94471,144.39842 113.77004,144.53486 L 113.08586,145.06919 112.75719,145.87328 V 145.87228 C 112.67349,146.07795 112.53808,146.25778 112.36238,146.39526 L 111.67819,146.92855 111.34953,147.73264 C 111.26583,147.93832 111.12939,148.11814 110.95472,148.25562 L 110.27053,148.78995 109.94186,149.59301 C 109.85816,149.79868 109.72276,149.97851 109.54705,150.11495 L 108.86493,150.64825 108.53627,151.45234 C 108.45257,151.65698 108.31612,151.83681 108.14145,151.97429 L 107.45727,152.50861 C 107.10381,153.3747 107.10794,153.38298 107.02629,153.51114 L 107.02729,153.51014 C 106.72241,152.88485 106.11263,152.46525 105.41913,152.4053 L 113.86092,141.24729 114.73529,141.90875 V 141.90975 C 114.96784,142.08545 115.23861,142.20328 115.52491,142.25392 Z'
    >>> separate_svg_path(s)
    ['M115.52497,142.25383', 'C115.44127,142.41816,115.3224,142.56184,115.1777,142.67553', 'L114.49352,143.20985,114.16485,144.01395', 'C114.08115,144.21859,113.94471,144.39842,113.77004,144.53486', 'L113.08586,145.06919,112.75719,145.87328', 'V145.87228', 'C112.67349,146.07795,112.53808,146.25778,112.36238,146.39526', 'L111.67819,146.92855,111.34953,147.73264', 'C111.26583,147.93832,111.12939,148.11814,110.95472,148.25562', 'L110.27053,148.78995,109.94186,149.59301', 'C109.85816,149.79868,109.72276,149.97851,109.54705,150.11495', 'L108.86493,150.64825,108.53627,151.45234', 'C108.45257,151.65698,108.31612,151.83681,108.14145,151.97429', 'L107.45727,152.50861', 'C107.10381,153.3747,107.10794,153.38298,107.02629,153.51114', 'L107.02729,153.51014', 'C106.72241,152.88485,106.11263,152.46525,105.41913,152.4053', 'L113.86092,141.24729,114.73529,141.90875', 'V141.90975', 'C114.96784,142.08545,115.23861,142.20328,115.52491,142.25392', 'Z']
    >>> s = 'M 98.625 26.939453 L 98.625 27.460938 C 98.754125 27.545773 98.879194 27.632457 99 27.722656 C 98.900475 27.452483 98.774716 27.19101 98.625 26.939453 z'
    >>> separate_svg_path(s)
    ['M98.625,26.939453', 'L98.625,27.460938', 'C98.754125,27.545773,98.879194,27.632457,99,27.722656', 'C98.900475,27.452483,98.774716,27.19101,98.625,26.939453', 'Z']
    """
    s = s.replace('z','Z')
    seg_types = ('M', 'S', 'L', 'Z', 'C', 'Q', 'A', 'H', 'V') # any others?

    sections = []
    curr_section = ''
    for char in s:
        if char in seg_types:
            sections.append(remove_svg_path_whitespace(curr_section))
            curr_section = ''
        curr_section += char
    sections.append(remove_svg_path_whitespace(curr_section))

    # check for implicit Ls
    refined_sections = []
    for seg in sections[1:]:
        # implicit L
        if ' ' in seg and seg[0] == 'M' and seg.count(',') > 1:
                #print('IMP:L', seg)
                spl = seg.split(' ')
                for i, substr in enumerate(spl):
                    if i == 0:
                        refined_sections.append(substr)
                    else:
                        l_sec = 'L' + substr
                        refined_sections.append(l_sec)
        else:
            seg = seg.replace(' ',',')
            refined_sections.append(seg)

    return refined_sections




def handle_implicit_path_coordinates(sections):
    """
    Go through the path, section by section, and turn implicit sections into explicit sections.
    :param sections: path, divided by section (e.g. C, L, Q)
    :return: list of [section type, list of coordinates]
    >>> s = 'M 106.14893,154.92896 105.12057,156.28805 C 105.12157,155.41162 104.84358,154.55791 104.32682,153.851 L 104.47152,153.65876 C 105.31488,152.54463 106.99228,153.81276 106.14892,154.92897 Z'
    >>> sections = separate_svg_path(s)
    >>> handle_implicit_path_coordinates(sections)
    [['M', [106.14893, 154.92896]], ['L', [105.12057, 156.28805]], ['C', [105.12157, 155.41162, 104.84358, 154.55791, 104.32682, 153.851]], ['L', [104.47152, 153.65876]], ['C', [105.31488, 152.54463, 106.99228, 153.81276, 106.14892, 154.92897]], ['Z', []]]
    """

    parsed = []
    for seg in sections:
        seg_type = seg[0]
        unsplit = seg[1:].strip()
        if len(unsplit) == 0:
            coords = []
        else:
            splitted = unsplit.split(',')
            coords = []
            for c in splitted:
                #assert c.replace('.','',1).isdigit(), seg + ':' + c
                assert str(float(c)) == c or c.count('e')==1 or str(int(c)) ==c, seg + ':' + c
                coords.append(float(c))

        if SEG_COORDS[seg_type] == len(coords):
            parsed.append( [seg_type, coords] )
        else:
            assert len(coords) % SEG_COORDS[seg_type] == 0
            n_extras = len(coords) // SEG_COORDS[seg_type]
            #print('PROBLEM', seg)
            start = 0
            for m in range(n_extras):
                #parsed.append(   )
                end = start + SEG_COORDS[seg_type]
                sub_coords = coords[start:end]
                assert len(sub_coords) == SEG_COORDS[seg_type]
                parsed.append( [seg_type, sub_coords] )
                #print('\t', seg_type, sub_coords, m)
                start = end
    return parsed


def parse_style_string(s):
    """
    Parse style information about a path.
    :param s: string
    :return: dictionary
    >>> parse_style_string('fill:#000000;stroke-width:0.264583')
    {'fill': '#000000', 'stroke-width': '0.264583'}
    >>> parse_style_string('fill:#000000')
    {'fill': '#000000'}
    """
    style = {}
    data = s.split(';')
    for a in data:
        key, val = a.split(':')
        style[key] = val
    return style


def parse_path_style(p, output_warnings=True):
    try:
        assert len(str(p['style'])) > 2
        return parse_style_string(p['style'])
    except:
        #print('Is Style?', 'style' in p, p)
        defaults = {'fill':'none', 'stroke':'none', 'stroke-width':0}

        for keyword in ['fill', 'stroke', 'stroke-width']:
            try:
                defaults[keyword] = p[keyword]
            except:
                if output_warnings:
                    print(f'Warning: no {keyword} found in path')

        return defaults


def draw_path(d, s, style, transform=''):
    """
    :param s:
    :return:
    >>> d = draw.Drawing(200, 200)
    >>> s = 'M 106.14893,154.92896 105.12057,156.28805 C 105.12157,155.41162 104.84358,154.55791 104.32682,153.851 L 104.47152,153.65876 C 105.31488,152.54463 106.99228,153.81276 106.14892,154.92897 Z'
    >>> y = {'fill': '#000000', 'stroke-width': '0.264583'}
    >>> draw_path(d, s, y)
    [['M', [106.14893, 154.92896]], ['L', [105.12057, 156.28805]], ['C', [105.12157, 155.41162, 104.84358, 154.55791, 104.32682, 153.851]], ['L', [104.47152, 153.65876]], ['C', [105.31488, 152.54463, 106.99228, 153.81276, 106.14892, 154.92897]], ['Z', []]]
    >>> d.save_svg('tests/test.svg')
    """
    fill = 'none'
    stroke = 'none'
    stroke_width = 0

    if 'fill' in style:
        fill = style['fill']
    if 'stroke' in style:
        stroke = style['stroke']
    if 'stroke-width' in style:
        stroke_width = style['stroke-width']

    if transform:
        p = draw.Path(fill=fill, stroke=stroke, stroke_width=stroke_width, transform=transform)
    else:
        p = draw.Path(fill=fill, stroke=stroke, stroke_width=stroke_width)

    #s = s.replace(' ','')
    sections = separate_svg_path(s)
    parsed = handle_implicit_path_coordinates(sections)

    for seg in parsed:
        seg_type, coords = seg
        assert SEG_COORDS[seg_type] == len(coords), seg
        if seg_type == 'M':
            p.M(*coords)
        elif seg_type == 'L':
            p.L(*coords)
        elif seg_type == 'C':
            p.C(*coords)
        elif seg_type == 'Q':
            p.Q(*coords)
        elif seg_type == 'S':
            p.T(*coords)
        elif seg_type == 'A':
            p.A(*coords)
        elif seg_type == 'H':
            p.H(*coords)
        elif seg_type == 'V':
            p.V(*coords)
        elif seg_type == 'Z':
            p.Z()
        else:
            assert True, seg

        #print(seg_type, SEG_COORDS[seg_type], len(coords), coords)
    d.append(p)
    return parsed


def import_svg(d, fname,
               x = 0, y = 0, wid = 100, hei=100,
               rounding_precision=3, rounding_func=round,
               make_new_drawing=False, id_name='import',
               group_transform='', fill='none', output_warnings=False):
    """
    Take a string representing an SVG path and turn it into a new string that
    represents the path in drawsvg.
    :param s: a path string. Must be all absolute.
    :return:
    >>> d = draw.Drawing(50, 50)
    >>> d = import_svg(d, 'assets/hacksaw.svg')
    >>> d.save_svg('tests/test2.svg')
    """
    svg_code = ''
    with open(fname, 'r') as f:
        svg_code = f.read()

    soup = BeautifulSoup(svg_code, 'xml')

    svg_width = float(soup.find('svg')['width'])
    svg_height = float(soup.find('svg')['height'])
    viewbox = soup.find('svg')['viewBox']
    if f'0 0 {svg_width} {svg_height}' != viewbox:
        if output_warnings:
            print('\tWARNING:VIEWBOX', viewbox, svg_width, svg_height, file=sys.stderr)

    if make_new_drawing:
        d = draw.Drawing(svg_width, svg_height)

    paths = soup.find_all('path')

    scale_x = wid / svg_width
    group_transform = f'translate({x}, {y}) scale({scale_x})'
    if group_transform:
        g = draw.Group(id=id_name, transform=group_transform)
    else:
        g = draw.Group(id=id_name)

    for p in paths:
        curr_path = p['d']
        style_dict = parse_path_style(p, output_warnings=output_warnings)
        try:
            transform = p['transform']
        except:
            transform = ''
        #print('\n', fname, style_dict)
        if fill != 'none':
            style_dict['fill'] = fill
        #print(fname, style_dict)
        draw_path(g, curr_path, style_dict, transform=transform)
    d.append(g)
    return d


def recreate_svg(input_fname, output_fname):
    """
    Recreate an SVG from input
    :param fname:
    :return:
    >>> recreate_svg('assets/hacksaw.svg', 'tests/test3.svg')
    >>> recreate_svg('assets/bear.svg', 'tests/test4.svg')
    Warning: no stroke found in path
    Warning: no stroke-width found in path
    >>> recreate_svg('assets/salt.svg', 'tests/test5.svg')
    >>> recreate_svg('assets/grill.svg', 'tests/test6.svg')
    """
    d = import_svg(None, input_fname, make_new_drawing=True)
    d.save_svg(output_fname)


if __name__ == '__main__':
    doctest.testmod()