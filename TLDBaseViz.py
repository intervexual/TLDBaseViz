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


class BaseLocation:
    def __init__(self, name, data, colours=()):
        """
        Set up a base as an object with a name, and a 2D list of BaseFeatures
        :param name: name of the base
        :param data: data from JSON file
        >>> b, c = parse_input('tests/testinput.json')
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
        self.connections = data[CONNECTIONS]


    def __repr__(self):
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
        margin_size = icon_size * margin_ratio
        cell_size = icon_size + margin_size
        box_width = margin_size*3 + cell_size * self.longest_row
        box_height = margin_size*3 + cell_size * (1 + len(self.features))
        self.box_width = box_width
        self.box_height = box_height
        return box_width, box_height, cell_size, margin_size
    def draw(self, d, icon_size, margin_ratio=1/8, x=0, y=0, fill='white', border='black'):
        """

        :param d:
        :param icon_size:
        :param margin_ratio:
        :return:
        >>> bases = process_input('tests/testinput.json')
        >>> w, h, c, m = bases['Quonset'].box_dimensions(20)
        >>> d = draw.Drawing(w, h)
        >>> bases['Quonset'].draw(d, 20)
        >>> d.save_svg('tests/quonset.svg')
        >>> w, h, c, m = bases['Misanthrope'].box_dimensions(20)
        >>> d = draw.Drawing(w, h)
        >>> bases['Misanthrope'].draw(d, 20)
        >>> d.save_svg('tests/misanthrope.svg')
        """
        box_width, box_height, cell_size, margin_size = self.box_dimensions(icon_size, margin_ratio)
        self.box_x = x
        self.box_y = y

        if self.indoors:
            rx = '0'
            ry = rx
        else:
            rx = str(icon_size)
            ry = rx
        if self.loading:
            stroke_dasharray = ''
        else:
            stroke_dasharray = '5,2'
        if self.customizable:
            stroke_opacity = 1
        else:
            stroke_opacity = .25

        d.append( draw.Rectangle(self.box_x+margin_size/2, self.box_y+margin_size/2,
                                 box_width-margin_size, box_height-margin_size,
                                 rx=rx, ry=ry, stroke_dasharray=stroke_dasharray,
                                 fill=fill, stroke_width=margin_size, stroke=border, stroke_opacity=stroke_opacity) )


        if self.indoors and self.customizable and self.num_features > 3:
            text_stroke = border
        else:
            text_stroke = 'none'

        font_size = box_width / 7
        text_x = x + box_width/2 #+ margin_size/2
        text_y = y + cell_size - margin_size * .5
        d.append( draw.Text(self.name, font_size, x=text_x, y=text_y,
                            text_decoration='bold',  text_anchor='middle', font_family='Arial', stroke=text_stroke,
                            fill=border, dominant_baseline='hanging',
                            textLength=box_width-cell_size, lengthAdjust='spacing') )

        icon_y = y + cell_size + margin_size*2
        for i, row in enumerate(self.features):
            icon_x = x + margin_size*2
            for j, bob in enumerate(row):
                import_svg(d, bob.filepath, x=icon_x, y=icon_y, wid=icon_size,
                           hei=icon_size, fill=bob.hex)

                # increment
                icon_x += cell_size
                #print(i,j, bob)
            icon_y += cell_size



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
    >>> b, c = parse_input('tests/testinput.json')
    >>> c
    {'base': 'oklch(0.4 0.06 150)', 'basebg': 'oklch(0.9 0.02 150)', 'bring': 'oklch(0.5 0.16 0)', 'todo': 'oklch(0.6 0.2 30)', 'tinder': 'oklch(0.4 0.06 50)', 'fir': 'oklch(0.6 0.14 70)', 'cedar': 'oklch(0.7 0.1 90)', 'cattail': 'oklch(0.5 0.08 110)', 'take': 'oklch(0.6 0.12 210)', 'destroy': 'oklch(0.5 0.2 250)', 'clearpath': 'oklch(0.7 0.18 270)', 'charcoal': 'oklch(0.1 0.04 290)', 'mixed': 'oklch(0.5 0.18 330)'}
    >>> b['Quonset']
    {'customizable': True, 'loading': True, 'indoors': True, 'features': ['bear,deer,wolf', 'workbench,Furniture,,BED,Bearbed,radio', 'Quality,Woodworking,Hacksaw,Hammer,Lantern', 'Curing,Curing,Curing,Curing,Cookpot,Cookpot', 'Curing,Curing,Curing,Curing,Skillet,Skillet', 'Trunk,Trunk,Trunk,Trunk,,Suitcase', 'Trunk,Trunk,Trunk,Trunk,,Suitcase'], 'connections': {'south': 'QMFishHut', 'east': 'LowerMine'}}
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    bases = data[BASES]
    colours = data[COLOURS]
    return bases, colours


def parse_colours(colours):
    """
    Convert strings in colours to hex strings in sRGB space
    :param colours: dict with name of colour, and colour probably formatted as oklch
    :return: same mappings but everything is hex codes
    >>> b, c = parse_input('tests/testinput.json')
    >>> parse_colours(c)
    {'base': '#2f5136', 'basebg': '#d5e2d7', 'bring': '#a62f5f', 'todo': '#de3e2d', 'tinder': '#623e29', 'fir': '#b17000', 'cedar': '#b79c51', 'cattail': '#66672d', 'take': '#0090a2', 'destroy': '#0065b0', 'clearpath': '#7997ff', 'charcoal': '#04010f', 'mixed': '#982f93'}
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


def process_input(filename='bases.json', to_print=False):
    """

    :param filename:
    :return:
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
    dict_keys(['LowerMine', 'UpperMine', 'Quonset', 'QMFishHut', 'Misanthrope', 'JMFishHut', 'Jackrabbit', 'JFFishHut', 'MidFishHuts', 'CommuterCar', 'Harris', 'No3Mine', 'No5Mine', 'Hibernia', 'BrokenBridge', 'Riken', 'LittleIsland'])
    """
    bases, colours = parse_input(filename)
    colours = parse_colours(colours)
    base_objects = {}
    for b in bases:
        bob = BaseLocation(b, bases[b], colours)
        base_objects[b] = bob
        if to_print:
            print(bob)
    return base_objects


def update_extremes(base_x, base_y, most_north, most_east, most_south, most_west):
    most_south = min(most_south, base_y)
    most_north = max(most_north, base_y)
    most_west = min(most_west, base_x)
    most_east = max(most_east, base_x)
    return most_north, most_east, most_south, most_west


def draw_bases(bases, icon_size=20, output='tests/bases.svg',
               base_x=200, base_y=100, width=800, height=600,
               arrow_colour='black', add_legend=True):
    """

    :param bases:
    :return:
    >>> bases = process_input('tests/testinput.json')
    >>> draw_bases(bases, add_legend=False)
    (557.5, 470.0)
    >>> bases = process_input('mybases.json')
    >>> draw_bases(bases, output='mybases.svg', width=2100, height=1400, base_x=1500, base_y=50)
    (1795.0, 1195.0)
    """
    d = draw.Drawing(width, height)
    d.append(draw.Rectangle(0,0,d.width,d.height,fill='white'))
    visited = []

    most_west = d.width
    most_east = 0
    most_south = d.height
    most_north = 0

    connections_made = {}

    for b in bases:
        arrow_size = icon_size
        #print('\n', b, '*'*35)
        bob = bases[b]
        w, h, c, m = bob.box_dimensions(icon_size)
        if b not in visited:
            g = draw.Group(id=b)
            bob.draw(g, icon_size, x=base_x, y=base_y)
            d.append(g)
            #print('\tDrawing', b)
            visited.append(b)
            most_north, most_east, most_south, most_west = update_extremes(base_x, base_y, most_north, most_east, most_south, most_west)

        if b not in connections_made:
            connections_made[b] = []

        # then the neighbours
        for dir in bob.connections:
            connection_name = bob.connections[dir]
            if connection_name not in connections_made[b]:
                cob = bases[connection_name]
                cob.box_dimensions(icon_size)
                p = draw.Path(stroke_width=m, stroke=arrow_colour)
                if dir == NORTH:
                    base_x = bob.box_x
                    line_x = base_x + m/2
                    base_y = bob.box_y
                    p.M(line_x, base_y)
                    if connection_name in visited:
                        arrow_size = bob.box_y - (cob.box_y + cob.box_height)
                    base_y = bob.box_y - arrow_size
                    p.L(line_x, base_y)
                    base_y -= cob.box_height
                    d.append(p)
                if dir == SOUTH:
                    base_x = bob.box_x
                    line_x = base_x + m/2
                    base_y = bob.box_y
                    p.M(line_x, base_y+bob.box_height)
                    if connection_name in visited:
                        arrow_size = cob.box_y - (bob.box_y + bob.box_height) #+ arrow_size
                    base_y += bob.box_height + arrow_size
                    p.L(line_x, base_y)
                    d.append(p)
                if dir == WEST:
                    base_y = bob.box_y
                    line_y = base_y + m/2
                    base_x = bob.box_x
                    p.M(base_x, line_y)
                    base_x -= arrow_size
                    p.L(base_x, line_y)
                    base_x -= cob.box_width
                    d.append(p)
                if dir == EAST:
                    base_x = bob.box_x + bob.box_width
                    base_y = bob.box_y
                    line_y = base_y + m/2
                    p.M(base_x, line_y)
                    if connection_name in visited:
                        arrow_size = cob.box_x - (bob.box_x + bob.box_width)
                    base_x += arrow_size
                    p.L(base_x, line_y)
                    d.append(p)
                connections_made[b].append(connection_name)
                if connection_name not in connections_made:
                    connections_made[connection_name] = []
                connections_made[connection_name].append(b)

                if connection_name not in visited:
                    ng = draw.Group(id=connection_name)
                    cob.draw(ng, icon_size, x=base_x, y=base_y)
                    d.append(ng)
                    #print('\tDrawing', connection_name)
                    most_north, most_east, most_south, most_west = update_extremes(base_x, base_y, most_north,
                                                                                   most_east, most_south, most_west)
                    visited.append(connection_name)

            #print(b, dir, bob.box_width, bob.box_height, bob.connections)
    counts = count_features(bases)
    draw_legend(d, x=arrow_size, y=0, counts=counts)

    d.save_svg(output)

    actual_height =  most_north - most_south
    actual_width = most_east - most_west
    #print( most_west, most_east,  most_south, most_north)
    return actual_width, actual_height


def count_features(bases, statuses_to_count=(ACTUAL, REMOVE)):
    """

    :param bases:
    :return:
    >>> bases = process_input('tests/testinput.json')
    >>> count_features(bases)
    {'bearbed': 0, 'bed': 5, 'forge': 1, 'milling': 0, 'furniture': 0, 'workbench': 2, 'trunk': 0, 'curing': 0, 'cookpot': 0, 'skillet': 0, 'potbelly': 4, 'grill': 0, 'range': 0, 'hacksaw': 0, 'quality': 3, 'lantern': 0, 'prybar': 0, 'woodworking': 0, 'hammer': 0, 'suitcase': 0, 'radio': 1, 'trader': 1, 'bear': 3, 'wolf': 3, 'poisonwolf': 0, 'deer': 5, 'rabbit': 2, 'ptarmigan': 0, 'moose': 0, 'timberwolf': 0, 'salt': 7, 'beachcombing': 6, 'coal': 4, 'fish': 4, 'birch': 0, 'empty': 3}
    >>> bases = process_input('mybases.json')
    >>> nums = count_features(bases)
    >>> nums['forge']
    4
    >>> nums['milling']
    2
    >>> nums['hacksaw']
    9
    >>> nums['woodworking']
    4
    >>> nums['hammer']
    7
    >>> nums['prybar']
    14
    >>> nums['lantern']
    6
    >>> nums['skillet']
    14
    >>> nums['cookpot']
    15
    >>> nums['radio']
    10
    >>> nums['salt']
    14
    >>> nums['birch']
    14
    >>> nums['range']
    7
    >>> total_bears = 2+4+3+1+3+0+1+0+0+2+2+2+0+0+1+2+3+0+1+3+0+0+1
    >>> total_bears - nums['bear']
    0
    >>> nums['moose'] >= 0
    True
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

    :param bases:
    :return:
    >>> bases = process_input('mybases.json')
    >>> verify_taking_numbers(bases)
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


def draw_legend(d, x=0, y=0, icon_size=20, margin_ratio=1/8, legend_colour='purple', counts=False):
    """
    Draw a legend
    :param d:
    :return:
    >>> d = draw.Drawing(200, 36*25)
    >>> d.append(draw.Rectangle(0, 0, d.width, d.height, fill='white'))
    >>> draw_legend(d)
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
                TRUNK:"rustic trunk", SUITCASE:"suitcase",
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



if __name__ == '__main__':
    doctest.testmod()