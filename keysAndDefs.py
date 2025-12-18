from utils import *

BASES = 'bases'
ACTUAL = 'actual'
PLANNED = 'planned'
REMOVE = 'remove'
NEARBY = 'nearby'
MAKE = 'make'
FIND = 'find'
BRING = 'bring'
TAKE = 'take'
DESTROY = 'destroy'

TOBRING = '+'
TOREMOVE = '-'
TOFIND = '?'
TOMAKE = '*'

PREFIXES = {TOBRING:BRING, TOREMOVE:REMOVE, TOFIND:FIND, TOMAKE:MAKE}

FEATURES = 'features'
CUSTOMIZABLE = 'customizable'
LOADING = 'loading'
CONNECTIONS = 'connections'
INDOORS = 'indoors'
EMPTY = 'empty'
EXPLORED = 'explored'
CABINFEVERRISK = 'cabinfeverrisk'

SOUTH = 'south'
NORTH = 'north'
EAST = 'east'
WEST = 'west'
BOTTOM = 'bottom'
TOP= 'top'
LEFT = 'left'
RIGHT = 'right'
REVERSE = {SOUTH:NORTH, NORTH:SOUTH, EAST:WEST, WEST:EAST, BOTTOM:TOP, TOP:BOTTOM, LEFT:RIGHT, RIGHT:LEFT}

# the colours provided
COLOURS = 'colours'
DASHES = 'dashes'
DESCRIPTIONS = 'descriptions'

BASE = 'base'
BASE_BG = 'basebg'
BG = 'bg'
OUTDOOR = 'outdoor'
FIR = 'fir'
CEDAR = 'cedar'
UNEXPLORED = FIND
PATH = 'path'

def parse_styling(fname):
    """
    Load the JSON file with the colour and dash scheme
    :param fname: filename
    :return: dict of colours, dict of dash styles
    >>> c, d, cs, ps = parse_styling('styling.json')
    >>> c['path']
    'oklch(0.7 0.1 170)'
    >>> d['path']
    ''
    >>> d['tinder']
    '4,2'
    >>> ps['tinder']
    'tinder path'
    >>> cs['destroy']
    'to destroy'
    """
    data = {}
    with open(fname, 'r') as f:
        data = json.load(f)
        assert type(data) == dict
    assert COLOURS in data
    assert DASHES in data

    colour_scheme = {}
    path_scheme = {}
    for k in data[DESCRIPTIONS]:
        if k in data[DASHES]:
            path_scheme[k] = data[DESCRIPTIONS][k]
        else:
            colour_scheme[k] = data[DESCRIPTIONS][k]

    return data[COLOURS], data[DASHES], colour_scheme, path_scheme


def parse_colours(colours):
    """
    Convert strings in colours to hex strings in sRGB space
    :param colours: dict with name of colour, and colour probably formatted as oklch
    :return: same mappings but everything is hex codes
    >>> c, d, cs, ps = parse_styling('styling.json')
    >>> parse_colours(c).keys()
    dict_keys(['bg', 'base', 'basebg', 'outdoor', 'bring', 'oneway', 'paint', 'tinder', 'fir', 'cedar', 'cattail', 'path', 'stone', 'take', 'destroy', 'clearpath', 'charcoal', 'mixed', 'find', 'todo'])
    >>> parse_colours(c)['tinder']
    '#623e29'
    """
    hexes = {}
    for c in colours:
        if 'oklch' in colours[c]:
            lchstr = colours[c].split('oklch(')[1].split(')')[0]
            if ' ' in lchstr:
                lchstr = lchstr.split(' ')
            else:
                lchstr = lchstr.split(',')

            assert len(lchstr) == 3, "impoperly formatted oklch colour"
            hex = oklch_to_hex(float(lchstr[0]), float(lchstr[1]), float(lchstr[2]))
        else:
            hex = colours[c]
        hexes[c] = hex
    return hexes


STYLE_FILE = 'styling.json'
raw_colours, DASHSTYLE, FILLS, STROKES = parse_styling(STYLE_FILE)
HEXES = parse_colours(raw_colours)

OUTDOOR_OPACITY = 0.25
FONTFAM = 'Arial'
KEYFONTFAM = 'Courier New'

CORN_X = 1
CORN_Y = 0
BIGNUM = 100000

PROBABILITY_DELIM = '/'
QTY_MARKER = ':'
TOTEXT = '#'
TABSIZE = 4

REGION = 'region'
INVENTORY = 'Inventory'
CURR_INVENTORY = 'CurrentInventory'
USED_UP = 'PermanentlyUsedUp'

TRUES = ['true', '''"true"''']

class LegendAsset:
    def __init__(self, key, descrip, group, theme, material, fixednum, movable, interloper, note='', extra=''):
        self.key = key
        self.filename = key + '.svg'
        self.description = descrip
        self.group = group
        self.theme = theme

        if not material: # TODO all of these
            material = BRING
        self.material = material

        if fixednum != '':
            fixednum = float(fixednum)
        self.fixednum = fixednum

        self.movable = movable.lower() in TRUES
        assert type(self.movable) is bool
        self.interloper = interloper.lower() in TRUES
    def __repr__(self):
        s = ':'.join([self.key, self.description, self.material, str(self.fixednum), str(self.movable)])
        return s


LEGEND = 'legend.csv'
COMMENT = '%'
DELIM = '\t'

ORDERING = {}
ASSETS = {EMPTY:'empty.svg'}
TODO_TYPES = {EMPTY:BASE}
MOVABLES = [EMPTY]
ICONS = []

with open(LEGEND, 'r') as f:
    for line in f:
        if not line.startswith(COMMENT):
            row = line.strip().split(DELIM)
            la = LegendAsset(*row)
            ICONS.append(la)
            ORDERING[la.key] = la.description
            ASSETS[la.key] = la.filename
            TODO_TYPES[la.key] = la.material
            if la.movable:
                MOVABLES.append(la.key)


if __name__ == '__main__':
    doctest.testmod()


