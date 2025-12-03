from keysAndDefs import *

class BaseFeature:
    def __init__(self, name, colours=()):
        """
        Create BaseFeature object with a name and material.
        :param name: case-sensitive name
        >>> str(BaseFeature('Trunk'))
        'trunk:fir'
        >>> str(BaseFeature('trunk'))
        'trunk:base'
        >>> str(BaseFeature('TRUNK'))
        'trunk:destroy'
        >>> str(BaseFeature('Workbench'))
        'workbench:cedar'
        >>> str(BaseFeature('Hammer'))
        'hammer:bring'
        >>> str(BaseFeature('HAMMER'))
        'hammer:take'
        >>> str(BaseFeature(''))
        'empty:base'
        """
        if not name:
            name = EMPTY

        self.original = name
        self.status = status_from_capitalization(name)
        self.name = name.lower()
        assert self.name in ASSETS
        if self.status == PLANNED:
            if self.name in TODO_TYPES:
                self.material = TODO_TYPES[self.name]
            else:
                self.material = BRING
        if self.status == ACTUAL:
            self.material = BASE
        if self.status == REMOVE:
            if self.name in MOVABLES:
                self.material = TAKE
            else:
                self.material = DESTROY

        # for drawing
        self.hex = '#000000'
        if colours:
            self.hex = colours[self.material]
        self.filepath = 'assets/' + ASSETS[self.name]
    def __repr__(self):
        return f'{self.name}:{self.material}'


class BaseConnection:
    def __init__(self, source, direction, source_corner, sink, sink_corner, kind, colours=False):
        """
        Create BaseConnection object, saving its destinations, corners, and kind of connection (road, rail, etc).
        :param source: name of source base
        :param direction: direction to sink (north, east, etc)
        :param source_corner: corner of source base's box to draw from, formatted like "top,right"
        :param sink: name of sink base
        :param sink_corner: corner of sink base's box to draw to, formatted like "bottom,left"
        :param kind: for styling the line (e.g. road, rail)
        """
        self.source = source
        self.sink = sink
        self.vertices = [source, sink]

        self.source_corner = source_corner
        self.sink_corner = sink_corner
        self.corners = {}
        self.corners[self.source] = source_corner.replace(' ','').split(',')
        self.corners[self.sink] = sink_corner.replace(' ','').split(',')

        self.direction = direction
        self.reverse = REVERSE[direction]

        self.kind = kind
        self.colour = 'green'
        self.dasharray = DASHSTYLE[kind]
        if colours:
            self.colour = colours[kind]
    def invert(self, colours):
        return BaseConnection(self.sink, self.reverse, self.sink_corner, self.source, self.source_corner, self.kind, colours)
    def __repr__(self):
        """
        Textual representation of the connection
        :return: representation as string
        >>> b, e, c = parse_input('tests/testinput.json')
        >>> edges = parse_edges(e)
        >>> hibernia_to_bear = edges['Hibernia']['BrokenBridge']
        >>> hibernia_to_bear
        BrokenBridge
        |
        Hibernia
        >>> edges['Hibernia']['Riken'] # reversing direction
        Hibernia
        |
        Riken
        >>> BaseConnection("Quonset", "south", "bottom,right", "CommuterCar", "top,right", "road") # right align
            Quonset
                  |
        CommuterCar
        >>> edges['MidFishHuts']['Jackrabbit'] # bottom (top,right) to top (bottom,left)
                  MidFishHuts
                 |
        Jackrabbit
        >>> edges['Riken']['LittleIsland']
        R -- L
        i    i
        k    t
        e    t
        n    l
             e
             I
             s
             l
             a
             n
             d
        >>> edges['Misanthrope']['JMFishHut']
        J -- M
        M    i
        F    s
        i    a
        s    n
        h    t
        H    h
        u    r
        t    o
             p
             e
        >>> edges['Quonset']['LowerMine']
        L
        o
        w
        e
        r
        M
        i
        n
        e -- Q
             u
             o
             n
             s
             e
             t
        """
        s = ''
        if self.direction in [NORTH, SOUTH]:
            top, bottom = self.sink, self.source
            if self.direction == SOUTH:
                bottom, top = self.sink, self.source

            len_diff = 0
            line_offset = 0
            if self.corners[bottom][CORN_X] == RIGHT:
                if self.corners[top][CORN_X] == RIGHT:
                    if len(bottom) > len(top):
                       len_diff = len(bottom) - len(top)
                    line_offset = len(top) + len_diff - 1
                if self.corners[top][CORN_X] == LEFT:
                    len_diff = len(bottom)
                    line_offset = len(bottom) - 1
                s += ' ' * len_diff

            s += top + '\n'
            s += ' '*(line_offset)
            s += '|\n'
            s += bottom
            return s

        if self.direction in [EAST, WEST]:
            left, right = self.sink, self.source
            if self.direction == EAST:
                right, left = self.sink, self.source

            if self.corners[left][CORN_Y] == TOP and self.corners[right][CORN_Y] == TOP:
                pad_left = left
                pad_right = right
                len_diff = len(right) - len(left)
                if len_diff >= 0:
                    pad_left = left + ' '*(abs(len_diff))
                else:
                    pad_right = right + ' '*(abs(len_diff))

                assert len(pad_left) == len(pad_right), f'{pad_left}, {pad_right}, {len(pad_left)}, {len(pad_right)}'

                for i in range(len(pad_left)):
                    if i == 0:
                        delim = ' -- '
                    else:
                        delim = ' '*4
                    s += pad_left[i] + delim + pad_right[i] + '\n'
                return s[:-1]

            if self.corners[left][CORN_Y] == BOTTOM and self.corners[right][CORN_Y] == TOP:
                for i in range((len(left))):
                    if i == len(left) - 1:
                        s += left[i] + ' -- ' + right[0] + '\n'
                    else:
                        s += left[i] + '\n'
                for i in range(len(right)-1):
                    s += ' '*5 + right[i+1] + '\n'

                return s[:-1]
            return f'{right}--{left}'



class BaseLocation:
    def __init__(self, name, data, colours=()):
        """
        Set up a base as an object with a name, and a 2D list of BaseFeatures
        :param name: name of the base
        :param data: data from JSON file
        >>> b, e, c = parse_input('tests/testinput.json')
        >>> b['Quonset'][FEATURES]
        ['bear,deer,wolf', 'workbench,Furniture,,BED,Bearbed,radio', 'Quality,Woodworking,Hacksaw,Hammer,Lantern', 'Curing,Curing,Curing,Curing,Cookpot,Cookpot', 'Curing,Curing,Curing,Curing,Skillet,Skillet', 'Trunk,Trunk,Trunk,Trunk,,Suitcase', 'Trunk,Trunk,Trunk,Trunk,,Suitcase']
        >>> quonset = BaseLocation('Quonset', b['Quonset'])
        >>> print(quonset)
        ------
        Quonset (C, L)
        ------
        [bear:base, deer:base, wolf:base]
        [workbench:base, furniture:cedar, empty:base, bed:destroy, bearbed:fir, radio:base]
        [quality:bring, woodworking:bring, hacksaw:bring, hammer:bring, lantern:bring]
        [curing:fir, curing:fir, curing:fir, curing:fir, cookpot:bring, cookpot:bring]
        [curing:fir, curing:fir, curing:fir, curing:fir, skillet:bring, skillet:bring]
        [trunk:fir, trunk:fir, trunk:fir, trunk:fir, empty:base, suitcase:bring]
        [trunk:fir, trunk:fir, trunk:fir, trunk:fir, empty:base, suitcase:bring]
        ------
        >>> mis = BaseLocation('Misanthrope', b['Misanthrope'])
        >>> print(mis)
        ---
        Misanthrope (C, L)
        ---
        [bear:base, deer:base, wolf:base]
        [salt:base, beachcombing:base]
        [bed:base, trader:base, quality:base]
        [workbench:cedar, furniture:cedar, bearbed:fir]
        ---
        """
        self.name = name
        self.is_drawn = False

        self.features = []
        self.customizable = data[CUSTOMIZABLE]
        self.loading = data[LOADING]
        self.indoors = data[INDOORS]

        self.num_features = 0
        assert FEATURES in data
        self.longest_row = 0
        # set up the features
        for row in data[FEATURES]:
            row_info = row.split(',')
            self.longest_row = max(self.longest_row, len(row_info))
            row_objects = []
            for feature in row_info:
                row_objects.append( BaseFeature(feature.strip(), colours) )
                if feature.strip() != EMPTY:
                    self.num_features += 1
            self.features.append(row_objects)

        # connections
        self.connections = {}
        self.edges = {}
        self.edges_drawn = {}
        if CONNECTIONS in data:
            for dir in data[CONNECTIONS]:
                sink_name = data[CONNECTIONS][dir]
                self.connections[sink_name] = dir
    def reset_drawing(self):
        self.is_drawn = False
        for e in self.edges_drawn:
            self.edges_drawn[e] = False
    def add_connection(self, boc):
        """
        Add connection/edge to/from this base
        :param boc: BaseConnection object
        :return:
        """
        self.connections[boc.sink] = boc.direction
        self.edges[boc.sink] = boc
        self.edges_drawn[boc.sink] = False
    def __repr__(self):
        """
        :return: Text representation for the base.
        """
        sizer = 1
        liner = '-' * self.longest_row*sizer + '\n'
        s = liner
        s += self.name
        if self.customizable and self.loading:
            s += ' (C, L)'
        elif self.customizable:
            s += ' (C)'
        elif self.loading:
            s += ' (L)'
        s += '\n'
        s += liner
        for row in self.features:
            s += str(row) + '\n'
        s += liner[:-1]
        return s
    def box_dimensions(self, icon_size, margin_ratio=1/8):
        """
        Calculate and save dimensions for drawing the base, derived from a given icon height in pixels
        :param icon_size: icon height in pixels (is square, so also its width)
        :param margin_ratio: margin between icons as a fraction of icon size
        :return: width of the box for the base, height, height of a given row in the box, margin size in pixels
        >>> bases = process_input('tests/testinput.json')
        >>> bases['Quonset'].box_dimensions(20)
        (142.5, 187.5, 22.5, 2.5)
        """
        self.icon_size = icon_size
        self.margin_size = icon_size * margin_ratio
        self.cell_size = icon_size + self.margin_size
        self.box_width = self.margin_size*3 + self.cell_size * self.longest_row
        self.box_height = self.margin_size*3 + self.cell_size * (1 + len(self.features))
        return self.box_width, self.box_height, self.cell_size, self.margin_size
    def draw_base_box(self, d, x=0, y=0, fill='white', border='black'):
        """
        Draw just the box for the base.
        :param d: drawing object
        :param x: upper left corner of box on canvas
        :param y: upper left corner of box on canvas
        :param fill: box fill colour
        :param border: box border colour
        :return:
        >>> bases = process_input('tests/testinput.json')
        >>> w, h, c, m = bases['Quonset'].box_dimensions(20)
        >>> d = draw.Drawing(w, h)
        >>> bases['Quonset'].draw_base_box(d)
        >>> d.save_svg('tests/quonset_box.svg')
        """
        self.box_x = x
        self.box_y = y

        rx = '0'
        ry = rx
        if not self.indoors:
            rx = str(self.icon_size)
            ry = rx

        stroke_dasharray = ''
        #if not self.loading:
        #    stroke_dasharray = '5,2'

        stroke_opacity = 1
        if not self.customizable:
            stroke_opacity = .25

        margin = self.margin_size/2
        self.box_top = self.box_y + margin
        self.box_left = self.box_x + margin
        self.box_right = self.box_left + self.box_width-self.margin_size
        self.box_bottom = self.box_top + self.box_height-self.margin_size

        d.append( draw.Rectangle(self.box_left, self.box_top,
                                 self.box_width-self.margin_size, self.box_height-self.margin_size,
                                 rx=rx, ry=ry, stroke_dasharray=stroke_dasharray, stroke_opacity=stroke_opacity,
                                 fill=fill, stroke_width=self.margin_size, stroke=border ) )
    def draw(self, d, icon_size, margin_ratio=1/8, x=0, y=0, fill='white', border='black'):
        """
        Draw the base with drawsvg
        :param d: Drawing object
        :param icon_size: icon height in pixels (square)
        :param margin_ratio: margin between icons, as a fraction of icon size
        :return:
        >>> bases = process_input('tests/testinput.json')
        >>> w, h, c, m = bases['Quonset'].box_dimensions(20)
        >>> d = draw.Drawing(w, h)
        >>> bases['Quonset'].draw(d, 20)
        >>> (bases['Quonset'].box_top, bases['Quonset'].box_bottom, bases['Quonset'].box_left, bases['Quonset'].box_right)
        (1.25, 186.25, 1.25, 141.25)
        >>> d.save_svg('tests/quonset.svg')
        >>> w, h, c, m = bases['Misanthrope'].box_dimensions(20)
        >>> d = draw.Drawing(w, h)
        >>> bases['Misanthrope'].draw(d, 20)
        >>> d.save_svg('tests/misanthrope.svg')
        """
        box_width, box_height, cell_size, margin_size = self.box_dimensions(icon_size, margin_ratio)
        g = draw.Group(id=self.name)
        self.draw_base_box(g, x=x, y=y, fill=fill, border=border)

        if self.indoors and self.customizable and self.num_features > 6:
            text_stroke = border
        else:
            text_stroke = 'none'

        # the title
        font_size = box_width / 7
        text_x = x + box_width/2 #+ margin_size/2
        text_y = y + cell_size - margin_size * .5
        g.append( draw.Text(self.name, font_size, x=text_x, y=text_y, text_anchor='middle',
                             font_family='Arial', stroke=text_stroke, fill=border) )

        # matrix of icons
        icon_y = y + cell_size + margin_size*2
        for i, row in enumerate(self.features):
            icon_x = x + margin_size*2
            for j, bob in enumerate(row):
                import_svg(g, bob.filepath, x=icon_x, y=icon_y, wid=icon_size,
                           hei=icon_size, fill=bob.hex)
                icon_x += cell_size
            icon_y += cell_size
        d.append(g)
        self.is_drawn = True

    def draw_connection(self, d, neighbour, arrow_ratio=1.0,
                        most_north=BIGNUM, most_south=0, most_west=BIGNUM, most_east=0):
        """
        Draw connection from self to neighbouring base
        :param d: drawing object
        :param neighbour: BaseLocation object
        :return:
        >>> b, e, colours = parse_input('tests/testinput.json')
        >>> colours = parse_colours(colours)
        >>> bases = process_input('tests/testinput.json')
        >>> w, h, c, m = bases['Hibernia'].box_dimensions(20)
        >>> d = draw.Drawing(w*3, h*3)
        >>> bases['Hibernia'].draw(d, 20, y=h, x=w)
        >>> (bases['Hibernia'].box_top, bases['Hibernia'].box_bottom, bases['Hibernia'].box_left, bases['Hibernia'].box_right)
        (98.75, 193.75, 76.25, 148.75)
        >>> [bases['Hibernia'].edges_drawn['Riken'], bases['Riken'].edges_drawn['Hibernia']]
        [False, False]
        >>> bases['Hibernia'].draw_connection(d, bases['Riken'])
        >>> [bases['Hibernia'].edges_drawn['Riken'], bases['Riken'].edges_drawn['Hibernia']]
        [True, True]
        >>> [bases['Hibernia'].edges_drawn['BrokenBridge'], bases['BrokenBridge'].edges_drawn['Hibernia']]
        [False, False]
        >>> bases['Hibernia'].draw_connection(d, bases['BrokenBridge'])
        >>> [bases['Hibernia'].edges_drawn['BrokenBridge'], bases['BrokenBridge'].edges_drawn['Hibernia']]
        [True, True]
        >>> bases['Hibernia'].draw_connection(d, bases['No5Mine'])
        >>> bases['Riken'].draw_connection(d, bases['LittleIsland'])
        >>> bases['No5Mine'].add_connection(BaseConnection("No5Mine", "east", "top,right", "BrokenBridge", "top,right", "road", colours))
        >>> bases['No5Mine'].draw_connection(d, bases['BrokenBridge'])
        >>> bases['Hibernia'].add_connection(BaseConnection("Hibernia", "west", "bottom,left", "No3Mine", "top,right", "tinder", colours))
        >>> bases['Hibernia'].draw_connection(d, bases['No3Mine'])
        >>> d.save_svg('tests/hibernia.svg')
        """
        neigh_name = neighbour.name
        arrow_size = self.cell_size*arrow_ratio
        most_north, most_south, most_west, most_east = update_extremes(self, most_north, most_south, most_west, most_east)

        cob = self.edges[neigh_name]
        assert cob.source == self.name

        if not self.edges_drawn[neigh_name]:
            p = draw.Path(stroke_width=self.margin_size, stroke=cob.colour, stroke_dasharray=cob.dasharray)

            assert cob.corners[self.name][CORN_Y] in [BOTTOM, TOP]
            if cob.corners[self.name][CORN_Y] == BOTTOM:
                source_y = self.box_bottom #+ self.margin_size/2
            else:
                source_y = self.box_top #- self.margin_size/2

            if cob.corners[self.name][CORN_X] == LEFT:
                source_x = self.box_left# - self.margin_size
            else:
                source_x = self.box_right

            p.M(source_x, source_y)

            if not neighbour.is_drawn:
                sink_x, sink_y = source_x, source_y
                if cob.direction == SOUTH:
                    sink_y += arrow_size
                if cob.direction == NORTH:
                    sink_y -= arrow_size
                if cob.direction == EAST:
                    sink_x += arrow_size
                if cob.direction == WEST:
                    sink_x -= arrow_size
                p.L(sink_x, sink_y)
                d.append(p)
                self.edges_drawn[neigh_name] = True
                neighbour.edges_drawn[self.name] = True

                neigh_left, neigh_top = sink_x, sink_y
                neighbour.box_dimensions(self.icon_size)
                if cob.corners[neigh_name][CORN_X] == LEFT:
                    neigh_left -=  self.margin_size/2
                if cob.corners[neigh_name][CORN_X] == RIGHT:
                    neigh_left -= neighbour.box_width
                    neigh_left +=  self.margin_size/2
                if cob.corners[neigh_name][CORN_Y] == BOTTOM:
                    neigh_top -= neighbour.box_height
                if cob.corners[neigh_name][CORN_Y] == TOP:
                    neigh_top -= self.margin_size/2

                #print('drawing child', self.name, neigh_name)
                neighbour.draw(d, self.icon_size, x=neigh_left, y=neigh_top)
            else:
                if cob.corners[neigh_name][CORN_Y] == BOTTOM:
                    sink_y = neighbour.box_bottom + self.margin_size/2
                else:
                    sink_y = neighbour.box_top - self.margin_size/2
                if cob.corners[neigh_name][CORN_X] == LEFT:
                    sink_x = neighbour.box_left
                else:
                    sink_x = neighbour.box_right
                p.L(sink_x, sink_y)
                d.append(p)
                #print('interpolating child', self.name, neigh_name)
                self.edges_drawn[neigh_name] = True
                neighbour.edges_drawn[self.name] = True



def status_from_capitalization(s):
    """
    Return whether the string is planned, actual, or to remove, based on capitalization.
    :param s: input string
    :return: status as string
    >>> status_from_capitalization('trunk')
    'actual'
    >>> status_from_capitalization('Trunk')
    'planned'
    >>> status_from_capitalization('TRUNK')
    'remove'
    """
    assert len(s) > 2, s
    if s.lower() == s:
        return ACTUAL
    if s.upper() == s:
        return REMOVE
    if s.capitalize() == s:
        return PLANNED
    assert True, s


def parse_input(filename='bases.json'):
    """
    Load JSON into dictionary format
    :param filename: input filename
    :return: dictionaries for base info & colour scheme
    >>> b, e, c = parse_input('tests/testinput.json')
    >>> c['base']
    'oklch(0.4 0.06 150)'
    >>> b['Quonset']
    {'customizable': True, 'loading': True, 'indoors': True, 'features': ['bear,deer,wolf', 'workbench,Furniture,,BED,Bearbed,radio', 'Quality,Woodworking,Hacksaw,Hammer,Lantern', 'Curing,Curing,Curing,Curing,Cookpot,Cookpot', 'Curing,Curing,Curing,Curing,Skillet,Skillet', 'Trunk,Trunk,Trunk,Trunk,,Suitcase', 'Trunk,Trunk,Trunk,Trunk,,Suitcase']}
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    bases = data[BASES]
    colours = data[COLOURS]
    edges = data[CONNECTIONS]
    return bases, edges, colours


def parse_colours(colours):
    """
    Convert strings in colours to hex strings in sRGB space
    :param colours: dict with name of colour, and colour probably formatted as oklch
    :return: same mappings but everything is hex codes
    >>> b, e, c = parse_input('tests/testinput.json')
    >>> parse_colours(c)
    {'base': '#2f5136', 'basebg': '#d5e2d7', 'bring': '#a62f5f', 'todo': '#de3e2d', 'tinder': '#623e29', 'fir': '#b17000', 'cedar': '#b79c51', 'cattail': '#66672d', 'rail': '#688e3b', 'path': '#76d3b4', 'take': '#0090a2', 'destroy': '#0065b0', 'clearpath': '#7997ff', 'charcoal': '#161227', 'road': '#6e5a7d', 'mixed': '#982f93'}
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


def parse_edges(edges, colours=False):
    """
    Convert the lists of edges from the JSON into BaseConnection objects.
    :return: dictionary, indexed by base names, each with a list of BaseConnection objects that go to/from the base.
    >>> b, e, c = parse_input('tests/testinput.json')
    >>> edges = parse_edges(e)
    >>> len(edges['Hibernia'])
    3
    >>> len(edges['Harris'])
    2
    >>> edges['LowerMine']['UpperMine']
    UpperMine
    |
    LowerMine
    >>> edges['UpperMine']['LowerMine']
    UpperMine
    |
    LowerMine
    >>> str(edges['No3Mine']['No5Mine']) == str(edges['No5Mine']['No3Mine'])
    True
    >>> edges['No3Mine']['No5Mine'] == edges['No5Mine']['No3Mine']
    False
    >>> parse_edges({})
    {}
    """
    connections = {}
    for e in edges:
        if type(e) != str:
            data = e
            if colours:
                data.append(colours)
            lob = BaseConnection(*data)
            rev_lob = lob.invert(colours)
            assert str(lob) == str(rev_lob), lob
            if lob.source not in connections:
                connections[lob.source] = {}
            connections[lob.source][lob.sink] = lob

            if lob.sink not in connections:
                connections[lob.sink] = {}
            connections[lob.sink][lob.source] = rev_lob # reverse it
    return connections


def process_input(filename='bases.json', to_print=False):
    """
    Parse input JSON and then turn it into BaseLocation objects.
    :param filename: input JSON filepath
    :return: list of BaseLocation objects.
    >>> bases = process_input('tests/testinput.json', to_print=False)
    >>> bases['Misanthrope']
    ---
    Misanthrope (C, L)
    ---
    [bear:base, deer:base, wolf:base]
    [salt:base, beachcombing:base]
    [bed:base, trader:base, quality:base]
    [workbench:cedar, furniture:cedar, bearbed:fir]
    ---
    >>> bases.keys()
    dict_keys(['UpperMine', 'LowerMine', 'Quonset', 'QMFishHut', 'Misanthrope', 'JMFishHut', 'Jackrabbit', 'JFFishHut', 'MidFishHuts', 'CommuterCar', 'Harris', 'No3Mine', 'No5Mine', 'Hibernia', 'BrokenBridge', 'Riken', 'LittleIsland'])
    """
    bases, edges, colours = parse_input(filename)
    colours = parse_colours(colours)
    edges = parse_edges(edges, colours)
    if len(edges) == 0:
        print('No edges! Old system!')
    base_objects = {}
    for b in bases:
        bob = BaseLocation(b, bases[b], colours)
        if b in edges:
            for connection_to_b in edges[b]:
                bob.add_connection(edges[b][connection_to_b])
        base_objects[b] = bob
        if to_print:
            print(bob)
    return base_objects


def update_extremes(bob, most_north, most_south, most_west, most_east):
    """
    Track the furthest dimensions that have been drawn thus far
    :param bob: BaseLocation object
    :param most_north: smallest y seen so far
    :param most_east: smallest x seen so far
    :param most_south: largest y seen so far
    :param most_west: largest x seen so far
    :return: updated values
    """
    assert bob.is_drawn
    most_south = max(most_south, bob.box_bottom)
    most_north = min(most_north, bob.box_top)
    most_west = min(most_west, bob.box_left)
    most_east = max(most_east, bob.box_right)
    return most_north, most_south, most_west, most_east


def graph_size(bases, most_north=BIGNUM, most_south = 0, most_west=BIGNUM, most_east=0):
    """
    Figure out the dimensions of the graph that was drawn
    :param bases: vertices in the graph, dictionary of base names : BaseLocation objects
    :return: width, height, min(x), max(x), min(y), max(y)
    >>> bases = process_input('tests/testinput.json')
    >>> draw_bases(bases, add_legend=False)
    >>> graph_size(bases)
    (607.5, 591.25, 106.25, 713.75, 51.25, 642.5)
    """
    for b in bases:
        bob = bases[b]
        most_north, most_south, most_west, most_east = update_extremes(bob, most_north, most_south, most_west, most_east)

    actual_height = most_south - most_north
    actual_width = most_east - most_west

    return actual_width, actual_height,  most_west, most_east, most_north, most_south


def redraw_bases(bases, icon_size=20, output='tests/rebases.svg', add_legend=True):
    """

    :param bases:
    :param icon_size:
    :param output:
    :return:
    >>> bases = process_input('tests/testinput.json')
    >>> draw_bases(bases, add_legend=False)
    >>> redraw_bases(bases, add_legend=False)
    """
    actual_width, actual_height, most_west, most_east, most_north, most_south = graph_size(bases)
    margin_size = icon_size
    new_width = actual_width + margin_size
    new_height = actual_height + margin_size

    # initial node
    parent = None
    for i, b in enumerate(bases):
        if i == 0:
            parent = bases[b]
    print(parent)
    print(parent.box_left, parent.box_right, parent.box_top, parent.box_bottom)

    # reset the drawn flags
    for b in bases:
        bob = bases[b]
        bob.reset_drawing()
    # TODO make use of the Use function for groups?
    # TODO do I need to calculate distance from initial node?
    draw_bases(bases, icon_size=icon_size, output=output, width=new_width, height=new_height)


def draw_bases(bases, icon_size=20, output='tests/bases.svg',
               base_x=200, base_y=50, width=800, height=700,
               add_legend=True):
    """
    Draw all bases
    :param bases:
    :return:
    >>> bases = process_input('tests/testinput.json')
    >>> draw_bases(bases, add_legend=False)
    """
    d = draw.Drawing(width, height)
    d.append(draw.Rectangle(0,0,d.width,d.height,fill='white'))
    visited = []

    gb = draw.Group(id='bases')

    for b in bases:
        arrow_size = icon_size
        #print('\n', b, '*'*35)
        bob = bases[b]
        w, h, c, m = bob.box_dimensions(icon_size)
        if not bob.is_drawn:
            g = draw.Group(id=b)
            bob.draw(g, icon_size, x=base_x, y=base_y)
            gb.append(g)
            #print('\tDrawing', b)
            visited.append(b)

        # then the neighbours
        for connection_name in bob.connections:
            dir = bob.connections[connection_name]
            bases[b].draw_connection(gb, bases[connection_name])

    d.append(gb)
    #d.append(draw.Use(gb, 0, 0))

    if add_legend:
        counts = count_features(bases)
        draw_legend(d, x=1900, y=10, counts=counts)

    d.save_svg(output)


def count_features(bases, statuses_to_count=(ACTUAL, REMOVE)):
    """
    For each feature (e.g. workbench, forge) count how many times it appears across the whole island.
    :param bases: list of BaseLocation objects
    :return: dictionary of counts, indexed by feature name (e.g. 'forge')
    >>> bases = process_input('tests/testinput.json')
    >>> count_features(bases)
    {'bearbed': 0, 'bed': 5, 'forge': 1, 'milling': 0, 'furniture': 0, 'workbench': 2, 'trunk': 0, 'curing': 0, 'cookpot': 0, 'skillet': 0, 'potbelly': 4, 'grill': 0, 'range': 0, 'hacksaw': 0, 'quality': 3, 'lantern': 0, 'prybar': 0, 'woodworking': 0, 'hammer': 0, 'suitcase': 0, 'radio': 1, 'trader': 1, 'bear': 3, 'wolf': 3, 'poisonwolf': 0, 'deer': 5, 'rabbit': 2, 'ptarmigan': 0, 'moose': 0, 'timberwolf': 0, 'salt': 7, 'beachcombing': 6, 'coal': 4, 'fish': 4, 'birch': 0, 'rockcache': 0, 'empty': 3}
    >>> bases = process_input('mybases.json')
    >>> nums = count_features(bases)
    >>> [nums['forge'], nums['milling'], nums['radio'], nums['trader'], nums['salt'], nums['range'], nums['woodworking']] # fixed for any given sandbox
    [4, 2, 10, 1, 14, 7, 4]
    >>> nums['birch'] > 13 and nums['birch'] < 16
    True
    >>> nums['hacksaw']
    9
    >>> nums['hammer']
    7
    >>> nums['prybar'] # TODO I should have 14, 16 but notes are inconsistent
    17
    >>> nums['lantern'] # 7 in world, I carry one with me
    6
    >>> nums['skillet']
    14
    >>> nums['cookpot'] == 15 - 2 # I carry two with me everywhere
    True
    >>> total_bears = 2+4+3+1+3+0+1+0+0+2+2+2+0+0+1+2+3+0+1+3+0+0+1
    >>> total_bears - nums['bear']
    0
    """
    count = {}
    for a in ASSETS:
        count[a] = 0

    for b in bases:
        for row in bases[b].features:
            for feature in row:
                if feature.status in statuses_to_count or feature.material in statuses_to_count:
                    count[feature.name] += 1
    return count


def verify_taking_numbers(bases):
    """
    Verify that for each feature, the number of items flagged as to-take equals the number of items flagged as to-bring.
    :param bases: list of BaseLocation objects
    :return:
    >>> bases = process_input('mybases.json')
    >>> verify_taking_numbers(bases)
    True
    """
    to_take = count_features(bases, statuses_to_count=[TAKE])
    to_bring = count_features(bases, statuses_to_count=[BRING])
    issues_found = False
    for a in to_bring:
        if to_bring[a] != to_take[a]:
            if not issues_found:
                print('key', 'to_bring', 'to_take', 'same?')
                issues_found = True
            print(a, to_bring[a], to_take[a], to_bring[a] == to_take[a])
    return not issues_found


def convert_edge_info(bases):
    """
    Convert edge information formatting for JSON
    :param bases: list of BaseLocation objects
    :return:
    >>> bases = process_input('mybases.json')
    >>> #convert_edge_info(bases)
    """
    connecs = []

    default_source = {NORTH:"top,left", SOUTH:"bottom,left", WEST:"top,left", EAST:"top,right"}
    default_sink = {NORTH:"bottom,left", SOUTH:"top,left", WEST:"top,right", EAST:"top,left"}

    for b in bases:
        bob = bases[b]
        for con in bob.connections:
            key = f'{b}:{con}'

            if key not in connecs:
                dir = bob.connections[con]
                data = [b, dir, default_source[dir], con, default_sink[dir], "todo"]
                s = '['
                for e in data:
                    s += f'''"{e}", '''
                s = s[:-2]  + '],'
                print(s)

                connecs.append(key)
                rev = f'{con}:{b}'
                connecs.append(rev)




def draw_legend(d, x=0, y=0, icon_size=20, margin_ratio=1/8, legend_colour='purple', counts=False):
    """
    Draw a legend
    :param d: drawing object
    :return: y position of the bottom of the legend
    >>> d = draw.Drawing(200, 36*25)
    >>> d.append(draw.Rectangle(0, 0, d.width, d.height, fill='white'))
    >>> draw_legend(d)
    860.0
    >>> d.save_svg('tests/legend.svg')
    """
    margin_size = icon_size * margin_ratio
    cell_size = icon_size + margin_size
    icon_y = y + cell_size + margin_size * 2
    icon_x = x + margin_size

    ordering = {BED:BED, BEAR_BED:"bear hide bed",
                WORK_BENCH:WORK_BENCH, FURN_BENCH:"furniture workbench", FORGE:FORGE, MILL_MACH:"milling machine",
                RADIO:"trader radio", TRADER:"trade drop-box",
                POTBELLY:"1-slot stove", GRILL:"2-slot stove", RANGE:"6-slot stove",
                COOKPOT:COOKPOT, SKILLET:SKILLET,
                LANTERN:LANTERN, QUALITY_TOOLS:"quality tools",
                HACKSAW:HACKSAW, HAMMER:"heavy hammer", PRYBAR:PRYBAR, WOODWORKING:"woodworking tools",
                TRUNK:"rustic trunk", SUITCASE:"suitcase", ROCK_CACHE:"rock cache",
                CURING_BOX:"curing box",
                SALT:"salt deposit",COAL:"coal",BEACHCOMBING:"beachcombing",BIRCH:"birch bark",
                BEAR:BEAR, MOOSE:MOOSE, DEER:DEER, WOLF:WOLF, POISON_WOLF:'poisoned wolf', TIMBERWOLF:TIMBERWOLF, RABBIT:RABBIT, PTARMIGAN:PTARMIGAN, FISH:'fishing'
    }
    assert  len(ASSETS) - len(ordering) <= 1, len(ASSETS) - len(ordering)

    legend_font_size = 10
    d.append(draw.Text('LEGEND', legend_font_size,
                       x=icon_x, y=icon_y + cell_size / 2,
                       fill=legend_colour))
    for i, a in enumerate(ordering):
        filepath = 'assets/' + ASSETS[a]
        icon_y += cell_size
        import_svg(d, filepath, x=icon_x, y=icon_y, wid=icon_size,
                   hei=icon_size, fill=legend_colour)
        d.append(draw.Text(ordering[a], legend_font_size,
                           x=icon_x+cell_size, y=icon_y+cell_size/2,
                           fill=legend_colour))
        if counts:
            count_x = icon_x + 5*cell_size
            d.append(draw.Text(str(counts[a]), legend_font_size,
                               x=count_x, y=icon_y+cell_size/2,
                               fill=legend_colour))
    return icon_y + cell_size


if __name__ == '__main__':
    doctest.testmod()

    if len(sys.argv) > 1:
        fname = sys.argv[1]
        print('Drawing', fname)
        if fname.endswith('.json'):
            outfile = fname.replace('.json', '.svg')
            bases = process_input(fname)
            # TODO automatically centre the base system rather than manually specifying
            draw_bases(bases, output=outfile, width=2100, height=1400, base_x=1600, base_y=35)
        else:
            print('To run: python3 TLDBaseViz.py mybases.json')