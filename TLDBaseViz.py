from keysAndDefs import *

class BaseFeature:
    def __init__(self, name, colours=(), probability=1):
        """
        Create BaseFeature object with a name and material.
        :param name: case-sensitive name
        >>> str(BaseFeature('+curing'))
        'curing:planned:bring'
        >>> str(BaseFeature('*trunk'))
        'trunk:planned:fir'
        >>> str(BaseFeature('trunk'))
        'trunk:actual:base'
        >>> str(BaseFeature('-trunk'))
        'trunk:actual:destroy'
        >>> str(BaseFeature('+workbench'))
        Traceback (most recent call last):
        ...
        AssertionError: +workbench is not movable
        >>> str(BaseFeature('+hammer'))
        'hammer:planned:bring'
        >>> str(BaseFeature('-hammer'))
        'hammer:actual:take'
        >>> str(BaseFeature(''))
        'empty:actual:base'
        >>> str(BaseFeature('#Blah'))
        'empty:actual:base'
        >>> str(BaseFeature('#+Blah'))
        'empty:planned:bring'
        """
        self.status, self.material = status_from_prefixes(name)

        self.alt_text = ''

        if not name or name.startswith(TOTEXT):
            if name.startswith(TOTEXT):
                self.alt_text = name
                for pref in PREFIXES:
                    if pref in self.alt_text and pref != TOTEXT:
                        self.alt_text = self.alt_text.replace(pref,'')
            name = EMPTY

        self.original = name
        self.probability = probability

        self.name = name.lower()
        for pref in PREFIXES:
            self.name = self.name.replace(pref, '')


        if PROBABILITY_DELIM in self.name:
            info = self.name.split(PROBABILITY_DELIM)
            self.name = info[0]
            self.probability = float(info[1])

        assert self.name in ASSETS, self.name
        if self.material == MAKE:
            if self.name in TODO_TYPES:
                self.material = TODO_TYPES[self.name]
            else:
                assert self.name in MOVABLES, f'{name} is not movable'
                print('Warning: old system used for bringing', name)
                self.material = BRING
        elif self.material == BRING:
            assert self.name in MOVABLES, f'{name} is not movable'
        elif self.material == REMOVE:
            if self.name in MOVABLES:
                assert self.name in MOVABLES, f'{name} is not movable'
                self.material = TAKE
            else:
                self.material = DESTROY

        # for drawing
        self.hex = '#000000'
        if colours:
            self.hex = colours[self.material]
        self.filepath = 'assets/' + ASSETS[self.name]
    def __repr__(self):
        return f'{self.name}:{self.status}:{self.material}'
    def draw(self, g, x=0, y=0, wid=20, hei=20, bg_colour=HEXES[BASE], opacity=0.5):
        if self.alt_text:
            font_size = font_size_for_box(self.alt_text, wid, hei)
            mid_y = y + hei/2
            mid_x = x + wid/2
            g.append(draw.Rectangle(x=x,y=y,width=wid,height=hei, fill='none', stroke=self.hex))
            g.append(draw.Text(self.alt_text, font_size,
                               x=mid_x, y=mid_y, fill=self.hex,
                               text_anchor='middle',
                               font_style='italic')) # , text_decoration='underline'
        else:
            import_svg(g, self.filepath, x=x, y=y, wid=wid,
                   hei=hei, fill=self.hex, opacity=self.probability) # shading for probabalistic features

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
        >>> b, e = parse_input('tests/testinput.json')
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
        >>> BaseConnection("Quonset", "south", "bottom,right", "CommuterCar", "top,right", "path") # right align
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
        >>> b, e = parse_input('tests/testinput.json')
        >>> b['Quonset'][FEATURES][0]
        'bear,deer,wolf'
        >>> quonset = BaseLocation('Quonset', b['Quonset'])
        >>> print(quonset)
        ------
        Quonset (C, L)
        ------
        [bear:actual:base, deer:actual:base, wolf:actual:base]
        [thermos:actual:base, thermos:actual:base, thermos:actual:base, thermos:actual:base, matches:actual:base, jerrycan:actual:base]
        [workbench:actual:base, furnbench:actual:base, bearbed:actual:base, radio:actual:base]
        [quality:actual:base, woodworking:actual:base, hammer:actual:base, prybar:actual:base, lantern:actual:base, hacksaw:actual:take]
        [curing:actual:base, curing:actual:base, curing:planned:fir, curing:planned:fir, cookpot:actual:base, cookpot:actual:base]
        [curing:actual:base, curing:actual:base, curing:planned:fir, curing:planned:fir, skillet:actual:base, skillet:actual:base]
        [trunk:actual:base, trunk:actual:base, trunk:actual:base, trunk:actual:base, rockcache:actual:base, suitcase:actual:base]
        [trunk:actual:base, trunk:actual:base, trunk:actual:base, trunk:planned:fir, rockcache:actual:base, suitcase:actual:base]
        [distress:actual:base, dpammo:actual:base, dpammo:actual:take, dpammo:actual:take, dpammo:actual:take, maglens:planned:bring]
        [quality:actual:take, quality:actual:take, quality:actual:take, quality:actual:take, quality:actual:take, vice:actual:take]
        ------
        >>> mis = BaseLocation('Misanthrope', b['Misanthrope'])
        >>> print(mis)
        ---
        Misanthrope (C, L)
        ---
        [bear:actual:base, deer:actual:base, wolf:actual:base]
        [salt:actual:base, beachcombing:actual:base]
        [bed:actual:base, trader:actual:base, quality:actual:base]
        [workbench:planned:cedar, furnbench:planned:cedar, bearbed:planned:fir]
        ---
        """
        self.name = name
        self.is_drawn = False

        self.features = []
        self.region = data[REGION]
        self.customizable = data[CUSTOMIZABLE]
        self.loading = data[LOADING]
        self.indoors = data[INDOORS]
        self.explored = data[EXPLORED]
        self.cabinfeverrisk = data[CABINFEVERRISK]
        if self.loading:
            assert self.cabinfeverrisk == True, f'{self.name} has loading screen and hence should have cabin fever risk'

        self.num_features = 0
        assert FEATURES in data
        self.longest_row = 0
        # set up the features
        if data[FEATURES] != '' and data[FEATURES] != ['']:
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
        >>> bases, colours = process_input('tests/testinput.json')
        >>> i = 20
        >>> bases['Harris'].longest_row
        1
        >>> bases['Harris'].box_dimensions(i)
        (42.5, 42.5, 22.5, 2.5)
        >>> bases['Quonset'].box_dimensions(20)
        (162.5, 265.0, 22.5, 2.5)
        >>> bases['CommuterCar'].longest_row
        0
        >>> bases['CommuterCar'].box_dimensions(20)
        (22.5, 22.5, 22.5, 2.5)
        """
        self.icon_size = icon_size
        self.margin_size = icon_size * margin_ratio
        self.cell_size = icon_size + self.margin_size

        border_and_margin = self.margin_size*4 #10
        minimal_text_header_height = self.margin_size*2

        # need at least this height
        feature_grid_height = self.cell_size*(len(self.features))
        self.box_height = feature_grid_height # 22.5 vs 90
        self.box_height += border_and_margin # +10 -> 32.5 vs 100
        self.box_height += minimal_text_header_height # + 5 -> 37.5 vs 105

        hei_times = math.ceil( self.box_height / icon_size ) # 2 vs 6
        self.box_height = hei_times * icon_size
        self.box_height += self.margin_size # for connection gridding

        if len(self.features) == 10:
            self.box_height += self.cell_size

        self.feature_grid_height = feature_grid_height

        # need at least this width
        self.box_width = self.cell_size*self.longest_row # 22.5
        self.box_width += border_and_margin # 32.5

        wei_times = math.ceil( self.box_width / icon_size ) # 2
        self.box_width = wei_times * icon_size
        self.box_width += self.margin_size # to allow for connections to be aligned when going downward from the right

        return self.box_width, self.box_height, self.cell_size, self.margin_size
    def draw_base_box(self, d, x=0, y=0,
                      fill=HEXES[BG], border=HEXES[BASE], outdoor=HEXES[OUTDOOR], unexplored=HEXES[UNEXPLORED]):
        """
        Draw just the box for the base.
        :param d: drawing object
        :param x: upper left corner of box on canvas
        :param y: upper left corner of box on canvas
        :param fill: box fill colour
        :param border: box border colour
        :return:
        >>> bases, colours = process_input('tests/testinput.json')
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
            stroke_opacity = OUTDOOR_OPACITY
        if not self.explored:
            border = unexplored

        margin = self.margin_size/2
        self.box_top = self.box_y + margin
        self.box_left = self.box_x + margin
        self.box_right = self.box_left + self.box_width-self.margin_size
        self.box_bottom = self.box_top + self.box_height-self.margin_size

        d.append( draw.Rectangle(self.box_left, self.box_top,
                                 self.box_width-self.margin_size, self.box_height-self.margin_size,
                                 rx=rx, ry=ry, stroke_dasharray=stroke_dasharray, stroke_opacity=stroke_opacity,
                                 fill=fill, stroke_width=self.margin_size, stroke=border ) )
    def draw_feature_grid(self, d, x=0, y=0, draw_guide_box=False):
        """
        Draw just the grid of features (icons like wolf, coal)
        :param d: drawing object
        :param x: top-left corner of the box on the canvas
        :param y: top-left corner of the box on the canvas
        :return: y-axis position for the top of the feature grid (useful for figuring out header height)
        >>> bases, colours = process_input('tests/testinput.json')
        >>> i = 20
        >>> w, h, c, m = bases['Harris'].box_dimensions(i)
        >>> d = draw.Drawing(w, h)
        >>> bases['Harris'].draw_base_box(d)
        >>> bases['Harris'].draw_feature_grid(d, 0, 0)
        17.5
        >>> d.save_svg('tests/harris.svg')
        """
        # matrix of icons
        g = draw.Group(id=self.name + ":features")

        box_bottom = y + self.box_height - self.margin_size
        self.feature_grid_top = box_bottom - self.feature_grid_height
        icon_y = self.feature_grid_top

        x_margin = self.box_width - self.cell_size*self.longest_row #- self.margin_size
        start_x = x + x_margin/2

        if draw_guide_box:
            g.append(draw.Rectangle(start_x, icon_y, self.cell_size*self.longest_row, self.cell_size*len(self.features), fill='none', stroke='green'))

        for i, row in enumerate(self.features):
            icon_x = start_x + self.margin_size/2
            for j, bob in enumerate(row):
                icon_group = draw.Group(id=f'{bob.name}:{self.name}:{j}:{i}')
                bob.draw(icon_group, x=icon_x, y=icon_y, wid=self.icon_size, hei=self.icon_size)
                g.append(icon_group)
                icon_x += self.cell_size
            icon_y += self.cell_size
        d.append(g)
        return self.feature_grid_top
    def draw_header(self, d, x=0, y=0, text_colour=HEXES[BASE], border=HEXES[BASE], unexplored=HEXES[UNEXPLORED]):
        """
        Draw just the grid of features (icons like wolf, coal)
        :param d: drawing object
        :param x: top-left corner of the box on the canvas
        :param y: top-left corner of the box on the canvas
        :return: y-axis position for the top of the feature grid (useful for figuring out header height)
        >>> bases, colours = process_input('tests/testinput.json')
        >>> i = 20
        >>> w, h, c, m = bases['Riken'].box_dimensions(i)
        >>> d = draw.Drawing(w, h)
        >>> bases['Riken'].draw_base_box(d)
        >>> bases['Riken'].draw_feature_grid(d, 0, 0)
        32.5
        >>> bases['Riken'].draw_header(d, 0, 0)
        >>> d.save_svg('tests/riken.svg')
        >>> d.save_png('tests/riken.png')
        >>> w, h, c, m = bases['MTFarm'].box_dimensions(i)
        >>> bases['MTFarm'].draw_base_box(d)
        >>> bases['MTFarm'].draw_feature_grid(d, 0, 0)
        27.5
        >>> bases['MTFarm'].draw_header(d, 0, 0)
        >>> d.save_svg('tests/mtfarm.svg')
        """
        g = draw.Group(id=self.name + ":header")

        min_text_top = y + 2 * self.margin_size
        max_text_bottom = self.feature_grid_top
        max_text_height = max_text_bottom - min_text_top

        max_text_width = self.box_width - self.margin_size * 4

        font_size = font_size_for_box(self.name,
                                      max_text_width, max_text_height)

        text_x = x + self.box_width / 2  # + margin_size/2
        high_possible = min_text_top + font_size - self.margin_size / 2
        low_possible = max_text_bottom - font_size / 2
        text_y = (high_possible + low_possible) / 2

        font_style = ''
        if not self.loading:
            font_style = 'italic'
        text_colour = border
        if not self.explored:
            text_colour = unexplored
        text_stroke = 'none'
        if self.indoors and self.customizable and self.num_features > 7:
            text_stroke = text_colour

        # dominant_baseline does not appear supported for SVG???????
        g.append( draw.Text(self.name,
                            font_size, font_family=FONTFAM,
                            stroke=text_stroke, font_style=font_style,
                            x=text_x, y=text_y, fill=text_colour,
                            text_anchor='middle' ) )
        d.append(g)

    def draw(self, d, icon_size, margin_ratio=1/8, x=0, y=0, fill=HEXES[BASE_BG], border=HEXES[BASE], unexplored=HEXES[UNEXPLORED]):
        """
        Draw the base with drawsvg
        :param d: Drawing object
        :param icon_size: icon height in pixels (square)
        :param margin_ratio: margin between icons, as a fraction of icon size
        :return:
        >>> bases, colours = process_input('tests/testinput.json')
        >>> w, h, c, m = bases['Quonset'].box_dimensions(20)
        >>> d = draw.Drawing(w, h)
        >>> bases['Quonset'].draw(d, 20)
        >>> (bases['Quonset'].box_top, bases['Quonset'].box_bottom, bases['Quonset'].box_left, bases['Quonset'].box_right)
        (1.25, 263.75, 1.25, 161.25)
        >>> d.save_svg('tests/quonset.svg')
        >>> w, h, c, m = bases['Misanthrope'].box_dimensions(20)
        >>> d = draw.Drawing(w, h)
        >>> bases['Misanthrope'].draw(d, 20)
        >>> d.save_svg('tests/misanthrope.svg')
        """
        box_width, box_height, cell_size, margin_size = self.box_dimensions(icon_size, margin_ratio)
        g = draw.Group(id=self.name)

        if self.region == INVENTORY:
            self.box_x = self.cell_size
            self.box_y = self.cell_size
            x = self.box_x
            y = self.box_y

        self.draw_base_box(g, x=x, y=y, fill=fill, border=border, unexplored=unexplored)
        self.draw_feature_grid(g, x=x, y=y)
        self.draw_header(g, x=x, y=y, border=border, unexplored=unexplored )

        d.append(g)
        self.is_drawn = True

    def draw_connection(self, d, neighbour, arrow_ratio=1.0,
                        most_north=BIGNUM, most_south=0, most_west=BIGNUM, most_east=0,
                        print_output=False,
                        unexplored=HEXES[UNEXPLORED], border=HEXES[BASE]):
        """
        Draw connection from self to neighbouring base
        :param d: drawing object
        :param neighbour: BaseLocation object
        :return:
        >>> bases, colours = process_input('tests/testinput.json')
        >>> w, h, c, m = bases['Hibernia'].box_dimensions(20)
        >>> d = draw.Drawing(w*3, h*3)
        >>> bases['Hibernia'].draw(d, 20, y=h, x=w)
        >>> (bases['Hibernia'].box_top, bases['Hibernia'].box_bottom, bases['Hibernia'].box_left, bases['Hibernia'].box_right)
        (123.75, 243.75, 103.75, 203.75)
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
        >>> bases['No5Mine'].add_connection(BaseConnection("No5Mine", "east", "top,right", "BrokenBridge", "top,left", "path", colours))
        >>> bases['No5Mine'].draw_connection(d, bases['BrokenBridge'])
        >>> bases['Hibernia'].add_connection(BaseConnection("Hibernia", "west", "bottom,left", "LonelyLighthouse", "top,right", "tinder", colours))
        >>> bases['Hibernia'].draw_connection(d, bases['LonelyLighthouse'])
        >>> d.save_svg('tests/hibernia.svg')
        """
        neigh_name = neighbour.name
        arrow_size = self.icon_size  # self.cell_size*arrow_ratio #
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
                    neigh_top += self.margin_size/2
                if cob.corners[neigh_name][CORN_Y] == TOP:
                    neigh_top -= self.margin_size/2

                if print_output:
                    print(' '*TABSIZE*2 + 'Drawing', neigh_name, "as child of", self.name)
                neighbour.draw(d, self.icon_size, x=neigh_left, y=neigh_top, unexplored=unexplored, border=border)
            else:
                if cob.corners[neigh_name][CORN_Y] == BOTTOM:
                    sink_y = neighbour.box_bottom #+ self.margin_size/2
                else:
                    sink_y = neighbour.box_top #- self.margin_size/2
                if cob.corners[neigh_name][CORN_X] == LEFT:
                    sink_x = neighbour.box_left
                else:
                    sink_x = neighbour.box_right
                p.L(sink_x, sink_y)
                d.append(p)

                if print_output:
                    print(' '*TABSIZE*2 + 'Connecting', self.name, "to", neigh_name)
                self.edges_drawn[neigh_name] = True
                neighbour.edges_drawn[self.name] = True


def font_size_for_box(s, max_text_width, max_text_height):
    # mid_text = (min_text_top + max_text_bottom)/2

    pixels_per_letter = max_text_width / len(s)
    font_size = pixels_per_letter * 1.5  # times 1.75 roughly fills the area, but is too tall
    # changing to 1.25 to ensure margins on the sides

    # print(self.name, max_text_bottom, max_text_height, max_text_width, font_size, pixels_per_letter)

    font_size = min(font_size, max_text_height)
    return font_size



def status_from_prefixes(s):
    """
    Return whether the string is planned, actual, or to remove, based on capitalization
    OR based on the string starting with +/-.
    :param s: input string
    :return: status as string
    >>> status_from_prefixes('trunk')
    ('actual', 'base')
    >>> status_from_prefixes('Trunk') # no longer supporting capitalization based status!
    ('actual', 'base')
    >>> status_from_prefixes('TRUNK')
    ('actual', 'base')
    >>> status_from_prefixes('-trunk')
    ('actual', 'remove')
    >>> status_from_prefixes('+Trunk')
    ('planned', 'bring')
    >>> status_from_prefixes('#+Trunk')
    ('planned', 'bring')
    >>> status_from_prefixes('-Trunk')
    ('actual', 'remove')
    >>> status_from_prefixes('#-Trunk')
    ('actual', 'remove')
    >>> status_from_prefixes('')
    ('actual', 'base')
    >>> status_from_prefixes('*trunk')
    ('planned', 'make')
    >>> status_from_prefixes('?trunk')
    ('planned', 'find')
    """
    if s == '':
        return ACTUAL, BASE

    was_to_text = False
    if s.startswith(TOTEXT):
        was_to_text = True
        s = s.replace(TOTEXT,'')

    if s.startswith(TOBRING):
        return PLANNED, BRING
    elif s.startswith(TOREMOVE):
        return ACTUAL, REMOVE
    elif s.startswith(TOFIND):
        return PLANNED, FIND
    elif s.startswith(TOMAKE):
        return PLANNED, MAKE

    return ACTUAL, BASE

def parse_input(filename='bases.json'):
    """
    Load JSON into dictionary format
    :param filename: input filename
    :return: dictionaries for base info & colour scheme
    >>> b, e = parse_input('tests/testinput.json')
    >>> b['Quonset']['indoors']
    True
    >>> b['Quonset']['region']
    'CoastalHighway'
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    bases = data[BASES]
    edges = data[CONNECTIONS]
    return bases, edges


def parse_edges(edges, colours=False):
    """
    Convert the lists of edges from the JSON into BaseConnection objects.
    :return: dictionary, indexed by base names, each with a list of BaseConnection objects that go to/from the base.
    >>> b, e = parse_input('tests/testinput.json')
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
    >>> bases, colours = process_input('tests/testinput.json', to_print=False)
    >>> bases['Misanthrope']
    ---
    Misanthrope (C, L)
    ---
    [bear:actual:base, deer:actual:base, wolf:actual:base]
    [salt:actual:base, beachcombing:actual:base]
    [bed:actual:base, trader:actual:base, quality:actual:base]
    [workbench:planned:cedar, furnbench:planned:cedar, bearbed:planned:fir]
    ---
    >>> bases.keys()
    dict_keys(['UpperMine', 'LowerMine', 'Quonset', 'QMFishHut', 'Misanthrope', 'JMFishHut', 'Jackrabbit', 'JFFishHut', 'MidFishHuts', 'CommuterCar', 'Harris', 'No3Mine', 'No5Mine', 'Hibernia', 'LonelyLighthouse', 'BrokenBridge', 'Riken', 'LittleIsland', 'MTFarm'])
    """
    bases, edges = parse_input(filename)
    colours = HEXES
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
    return base_objects, colours


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
    >>> bases, colours = process_input('tests/testinput.json')
    >>> draw_bases(bases, colours, add_legend=False)
    >>> graph_size(bases)
    (660.0, 822.5, 101.25, 761.25, 11.25, 833.75)
    """
    for b in bases:
        bob = bases[b]
        most_north, most_south, most_west, most_east = update_extremes(bob, most_north, most_south, most_west, most_east)

    actual_height = most_south - most_north
    actual_width = most_east - most_west

    return actual_width, actual_height,  most_west, most_east, most_north, most_south


def redraw_bases(bases, colours, icon_size=20, output='tests/rebases.svg', add_legend=True):
    """
    Redraw all the bases but nicely centred on the canvas. Not yet working.
    :param bases:
    :param icon_size:
    :param output:
    :return:
    >>> bases, colours = process_input('tests/testinput.json')
    >>> draw_bases(bases, colours, add_legend=False)
    >>> #redraw_bases(bases, colours, add_legend=False)
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
    draw_bases(bases, colours, icon_size=icon_size, output=output, width=new_width, height=new_height)


def draw_bases(bases, colours, icon_size=20, output='tests/bases.svg',
               base_x=200, base_y=150, width=800, height=800,
               add_legend=True, output_png=True, print_output=False):
    """
    Draw all bases
    :param bases:
    :return:
    >>> bases, edges = process_input('tests/testinput.json')
    >>> colours = HEXES
    >>> draw_bases(bases, colours, add_legend=False, print_output=True)
    Visiting UpperMine
        Drawing UpperMine
            Drawing LowerMine as child of UpperMine
            Drawing MTFarm as child of UpperMine
    Visiting LowerMine
            Drawing Quonset as child of LowerMine
    Visiting Quonset
            Drawing QMFishHut as child of Quonset
    Visiting QMFishHut
            Drawing Misanthrope as child of QMFishHut
            Drawing MidFishHuts as child of QMFishHut
    Visiting Misanthrope
            Drawing CommuterCar as child of Misanthrope
            Drawing JMFishHut as child of Misanthrope
    Visiting JMFishHut
            Drawing Jackrabbit as child of JMFishHut
    Visiting Jackrabbit
            Drawing JFFishHut as child of Jackrabbit
            Connecting Jackrabbit to MidFishHuts
    Visiting JFFishHut
            Connecting JFFishHut to MidFishHuts
    Visiting MidFishHuts
    Visiting CommuterCar
            Drawing Harris as child of CommuterCar
    Visiting Harris
            Drawing No3Mine as child of Harris
    Visiting No3Mine
            Drawing No5Mine as child of No3Mine
    Visiting No5Mine
            Drawing Hibernia as child of No5Mine
    Visiting Hibernia
            Drawing BrokenBridge as child of Hibernia
            Drawing Riken as child of Hibernia
    Visiting LonelyLighthouse
        Drawing LonelyLighthouse
    Visiting BrokenBridge
    Visiting Riken
            Drawing LittleIsland as child of Riken
    Visiting LittleIsland
    Visiting MTFarm
    """
    d = draw.Drawing(width, height)
    d.append(draw.Rectangle(0,0,d.width,d.height,fill=colours[BG]))
    visited = []

    gb = draw.Group(id='bases')
    unexplored_colour = colours[UNEXPLORED]

    for b in bases:
        if print_output:
            print('Visiting', b)
        arrow_size = icon_size
        #print('\n', b, '*'*35)
        bob = bases[b]
        w, h, c, m = bob.box_dimensions(icon_size)
        if not bob.is_drawn:
            g = draw.Group(id=b)
            bob.draw(g, icon_size, x=base_x, y=base_y, unexplored=unexplored_colour, border=colours[BASE])
            gb.append(g)
            if print_output:
                print(' '*TABSIZE + 'Drawing', b)
            visited.append(b)

        # then the neighbours
        for connection_name in bob.connections:
            if connection_name in bases:
                dir = bob.connections[connection_name]
                bases[b].draw_connection(gb, bases[connection_name], unexplored=unexplored_colour, border=colours[BASE], print_output=print_output)
            else:
                print('Warning: connected base not in bases', connection_name)

    d.append(gb)
    #d.append(draw.Use(gb, 0, 0))

    if CURR_INVENTORY in bases:
        to_bring, to_take = verify_taking_numbers(bases)
        out_bring = 'outstanding bring'
        out_take = 'outstanding take'
        bob = special_base(bases, out_bring, to_bring, CURR_INVENTORY, SOUTH)
        tob = special_base(bases, out_take, to_take, out_bring, SOUTH)
        bases[CURR_INVENTORY].draw_connection(d, bob, unexplored=colours[TAKE], border=colours[TAKE])
        bases[out_bring].draw_connection(d, tob, unexplored=colours[BRING], border=colours[BRING])

    if add_legend:
        counts = count_features(bases)
        draw_legend(d, colours, x=d.width-210, y=190, counts=counts)


    d.save_svg(output)
    if output_png:
        d.save_png(output.replace('.svg','.png'))


def draw_region(region, source_info, output='tests/', print_output=False):
    """
    Draw only the bases of one region.
    :param region: region name as string, e.g. 'AshCanyon'
    :param source_info: input json filename
    :return:
    >>> draw_region('AshCanyon', 'mybases.json', print_output=False)
    Warning: connected base not in bases EchoRavine
    Warning: connected base not in bases CaveFromAC
    >>> draw_region('TimberwolfMountain', 'mybases.json', print_output=False)
    Warning: connected base not in bases CaveToAC
    Warning: connected base not in bases Joplin
    Warning: connected base not in bases CaveToBRM
    Warning: connected base not in bases BitterMarshFishHut
    >>> draw_region('Blackrock', 'mybases.json', print_output=False)
    Warning: connected base not in bases Foresters
    Warning: connected base not in bases CaveFromBRM
    >>> draw_region('PleasantValley', 'mybases.json', print_output=False)
    Warning: connected base not in bases Mountaineer
    Warning: connected base not in bases KPSTrailer
    Warning: connected base not in bases CaveFromPV
    Warning: connected base not in bases UpperMineFromCH
    >>> draw_region('MountainTown', 'mybases.json', print_output=False)
    Warning: connected base not in bases MarshRidgeCave
    Warning: connected base not in bases Trapper
    Warning: connected base not in bases CaveToHRV
    >>> draw_region('MysteryLake', 'mybases.json', print_output=False)
    Warning: connected base not in bases WestRavineCave
    Warning: connected base not in bases CaveFromPV
    Warning: connected base not in bases Poacher
    Warning: connected base not in bases CaveToMT
    >>> draw_region('ForlornMuskeg', 'mybases.json', print_output=False)
    Warning: connected base not in bases MLRailTunnel
    Warning: connected base not in bases BRRailTunnel
    Warning: connected base not in bases HermitsCabin
    Warning: connected base not in bases CaveToBI
    """
    bases, colours = process_input(source_info)
    these_bases = {}

    output = output + region + '.svg'

    for b in bases:
        bob = bases[b]
        if bob.region == region:
            these_bases[b] = bob

    draw_bases(these_bases, colours,
               base_x = 500, base_y = 400,
               width = 1000, height = 1000,
               add_legend=False, print_output=print_output,
               output=output, output_png=False)


def count_features(bases, statuses_to_count=(ACTUAL, REMOVE)):
    """
    For each feature (e.g. workbench, forge) count how many times it appears across the whole island.
    :param bases: list of BaseLocation objects
    :return: dictionary of counts, indexed by feature name (e.g. 'forge')
    >>> bases, colours = process_input('tests/testinput.json')
    >>> type(count_features(bases))
    <class 'dict'>
    >>> bases, colours = process_input('mybases.json')
    >>> nums = count_features(bases)
    >>> [nums['forge'], nums['milling'], nums['radio'], nums['trader'], nums['salt'], nums['range'], nums['woodworking']] # fixed for any given sandbox
    [4, 2, 10, 2, 14, 7, 4]
    >>> nums['birch'] > 13 and nums['birch'] < 16
    True
    >>> nums['hacksaw']
    9
    >>> nums['hammer']
    7
    >>> nums['prybar'] # TODO I should have 14, 16 but notes are inconsistent
    20
    >>> nums['lantern'] + nums['spelunker'] # 7 in world, I carry one with me
    7
    >>> nums["firestriker"] # 4 in world, I carry one with me. None at Trapper or Quonset.
    4
    >>> nums["maglens"] # 3 in world, I carry one with me
    3
    >>> nums['skillet']
    14
    >>> nums['cookpot'] == 16 #- 2 # I carry two with me everywhere
    True
    >>> nums['thermos'] == 7 #- 2 # I carry two with me everywhere
    True
    >>> total_bears = 2+(3+.25)+3+1+3+0+1+0+0+2+2+2+0+0+(0.7)+2+3+0+1+3+0+0+1
    >>> total_bears - nums['bear']
    0.0
    >>> total_workbenches = 3+5+(1)+2+3+2+1+(4)+1+2+6+(4)+1+0+2+8+3+0
    >>> total_workbenches - nums['workbench'] # three known vices that have not been made into workbenches yet
    3
    >>> cedar_counts = count_features(bases, [CEDAR])
    >>> cedar_counts['workbench'] == nums['vice']
    True
    """
    count = {}
    for a in ASSETS:
        count[a] = 0

    for b in bases:
        for row in bases[b].features:
            for feature in row:
                if feature.status in statuses_to_count or feature.material in statuses_to_count:
                    count[feature.name] += feature.probability
    return count


def verify_taking_numbers(bases):
    """
    Verify that for each feature, the number of items flagged as to-take equals the number of items flagged as to-bring.
    :param bases: list of BaseLocation objects
    :return: list of unaccounted things to take, list of unaccounting things to bring
    >>> bases, colurs = process_input('mybases.json')
    >>> t, b = verify_taking_numbers(bases)
    >>> len(b) == 0
    True
    """
    to_take = count_features(bases, statuses_to_count=[TAKE])
    to_bring = count_features(bases, statuses_to_count=[BRING])
    issues_found = False
    unknown_take = []
    unknown_bring = []
    for a in to_bring:
        if to_bring[a] != to_take[a]:
            if a != EMPTY:
                if not issues_found:
                    issues_found = True
                diff = to_bring[a] - to_take[a]

                posn = '+'
                if diff > 0:
                    posn = '-'

                to_add = ','.join(abs(math.ceil(diff)) * [posn + a])
                if diff > 0:
                    unknown_take += [to_add]
                else:
                    unknown_bring += [to_add]

    return unknown_take, unknown_bring


def convert_edge_info(bases):
    """
    Convert edge information formatting for JSON
    :param bases: list of BaseLocation objects
    :return:
    >>> bases, colours = process_input('mybases.json')
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




def draw_legend(d, colours, x=0, y=0, icon_size=10, margin_ratio=1/8, legend_colour='purple', counts=False, background_colour='white'):
    """
    Draw a legend
    :param d: drawing object
    :return: y position of the bottom of the legend
    >>> d = draw.Drawing(200, (36+12)*25)
    >>> d.append(draw.Rectangle(0, 0, d.width, d.height, fill='white'))
    >>> bases, colours = process_input('mybases.json')
    >>> draw_legend(d, colours, icon_size=20)
    1512.5
    >>> d.save_svg('tests/legend.svg')
    """
    margin_size = icon_size * margin_ratio
    cell_size = icon_size + margin_size
    icon_y = y + cell_size + margin_size * 2
    icon_x = x + margin_size

    assert  len(ASSETS) - len(ORDERING) <= 1, len(ASSETS) - len(ORDERING)

    longest_name_len = 0
    for k in ORDERING:
        longest_name_len = max( len(ORDERING[k]), longest_name_len )

    legend_font_size = 10
    d.append(draw.Text('LEGEND', legend_font_size, font_family=FONTFAM,
                       x=icon_x, y=icon_y + cell_size / 2,
                       fill=legend_colour, stroke=legend_colour))
    for i, a in enumerate(ORDERING):
        filepath = 'assets/' + ASSETS[a]

        to_draw = True
        if counts: # don't draw if there are none in the data
            if counts[a] == 0:
                to_draw = False
        if to_draw:
            icon_y += cell_size
            text_y = icon_y + cell_size / 2 + margin_size
            import_svg(d, filepath, x=icon_x, y=icon_y, wid=icon_size,
                       hei=icon_size, fill=legend_colour)
            d.append(draw.Text(ORDERING[a], legend_font_size, font_family=FONTFAM,
                               x=icon_x+cell_size, y=text_y,
                               fill=legend_colour))
            if counts:
                count_x = icon_x + longest_name_len*(icon_size/2) + 4*margin_size
                d.append(draw.Text(str(round(counts[a],2)), legend_font_size, font_family=FONTFAM,
                                   x=count_x, y=text_y,
                                   fill=legend_colour))

    icon_y += cell_size
    text_y += cell_size
    import_svg(d, 'assets/bear.svg', x=icon_x, y=icon_y, wid=icon_size,
               hei=icon_size, fill=legend_colour, opacity=0.5)
    pb = 'opacity indicates probability (0.5 -> 50%)'
    d.append(draw.Text(pb, legend_font_size, font_family=FONTFAM,
                       x=icon_x + cell_size, y=text_y,
                       fill=legend_colour))

    colour_types = FILLS
    for j, a in enumerate(colour_types):
        icon_y += cell_size
        text_y += cell_size
        d.append(draw.Rectangle(fill=colours[a], x=icon_x, y=icon_y, width=icon_size, height=icon_size))
        d.append(draw.Text(colour_types[a], legend_font_size, font_family=FONTFAM,
                           x=icon_x+cell_size, y=text_y,
                           fill=legend_colour))

    path_types = STROKES
    for j, a in enumerate(path_types):
        icon_y += cell_size
        text_y += cell_size
        p = draw.Path(stroke=colours[a], stroke_width=margin_size, stroke_dasharray=DASHSTYLE[a] )
        p.M(icon_x, icon_y+cell_size/2)
        p.L(icon_x+icon_size, icon_y+cell_size/2)
        d.append(p)
        d.append(draw.Text(path_types[a], legend_font_size, font_family=FONTFAM,
                           x=icon_x+cell_size, y=text_y,
                           fill=legend_colour))

    icon_y += cell_size
    text_y += cell_size
    d.append(draw.Rectangle(fill='none', stroke=colours[BASE], x=icon_x, y=icon_y, width=icon_size, height=icon_size))
    d.append(draw.Text('customizable indoor location', legend_font_size, font_family=FONTFAM,
                       x=icon_x+cell_size, y=text_y,
                       fill=legend_colour))

    icon_y += cell_size
    text_y += cell_size
    d.append(draw.Rectangle(fill='none', stroke=colours[BASE], x=icon_x, y=icon_y, width=icon_size, height=icon_size, opacity=OUTDOOR_OPACITY))
    d.append(draw.Text('non-customizable indoor location', legend_font_size, font_family=FONTFAM,
                       x=icon_x+cell_size, y=text_y,
                       fill=legend_colour))


    icon_y += cell_size
    text_y += cell_size
    d.append(draw.Rectangle(fill='none', stroke=colours[BASE], x=icon_x, y=icon_y, width=icon_size, height=icon_size,
                            rx=icon_size/2.5, ry=icon_size/2.5, opacity=OUTDOOR_OPACITY))
    d.append(draw.Text('outdoors (cannot cure hides)', legend_font_size, font_family=FONTFAM,
                       x=icon_x+cell_size, y=text_y,
                       fill=legend_colour))

    icon_y += cell_size
    text_y += cell_size
    #d.append(draw.Rectangle(fill='none', stroke=colours[BASE], x=icon_x, y=icon_y, width=icon_size, height=icon_size, opacity=OUTDOOR_OPACITY))
    d.append(draw.Text('italics mean no loading screen', legend_font_size, font_family=FONTFAM,
                       x=icon_x+cell_size, y=text_y,
                       fill=legend_colour, font_style='italic'))

    return icon_y + cell_size


def legends_for_documentation(icon_wid=50):
    """
    Make legends of the icons for documentation purposes.
    :return:
    >>> legends_for_documentation()
    """
    group_n = {}
    group_cols = {}
    theme_n = {}

    for lob in ICONS:
        if lob.group not in group_n:
            group_n[lob.group] = 0
            group_cols[lob.group] = []
        if lob.theme not in theme_n:
            theme_n[lob.theme] = 0

        group_n[lob.group] += 1
        group_cols[lob.group].append(lob.theme)
        theme_n[lob.theme] += 1

    group_max_cols = {}
    group_max_rows = {}
    for g in group_n:
        uniques = list(set(group_cols[g]))
        group_max_rows[g] = len(uniques)
        max_cols = 0
        for u in uniques:
            curr_count = group_cols[g].count(u)
            max_cols = max(max_cols, curr_count)
        group_max_cols[g] = max_cols

    cell_wid = icon_wid * (1 + 1 / 8)
    text_factor = 1/3
    text_hei = icon_wid*text_factor
    cell_hei = cell_wid + text_hei*3

    legend_colour = 'black'

    for g in group_n:
        d = draw.Drawing(cell_wid * group_max_cols[g], cell_hei*group_max_rows[g])
        d.append(draw.Rectangle(0,0,d.width,d.height, fill='white'))
        #print(g, group_n[g], group_cols[g])
        start_x =  (cell_wid - icon_wid)/2
        icon_x = start_x
        text_x = start_x + icon_wid/2
        icon_y = start_x
        text_y = icon_y + cell_wid + text_hei/3

        latest_theme = ''

        for lob in ICONS:
            if lob.group == g:
                if lob.theme != latest_theme:
                    if latest_theme:
                        icon_y += cell_hei
                        text_y += cell_hei
                        icon_x = start_x
                        text_x = start_x + icon_wid / 2
                    latest_theme = lob.theme

                fill_colour = legend_colour
                if not lob.interloper:
                    fill_colour = 'green'

                import_svg(d, 'assets/' + lob.filename, x=icon_x, y=icon_y, wid=icon_wid,
                           hei=icon_wid, fill=fill_colour)

                legend_font_size = font_size_for_box(lob.description, icon_wid, text_hei)
                key_str = '"'+ lob.key + '"'
                key_font_size = font_size_for_box(key_str, icon_wid, text_hei)

                d.append(draw.Text(lob.description, legend_font_size, font_family=FONTFAM,
                                   x=text_x, y=text_y, text_anchor='middle',
                                   fill=fill_colour))
                d.append(draw.Text(key_str, key_font_size, font_family=KEYFONTFAM,
                                   x=text_x, y=text_y+text_hei, text_anchor='middle',
                                   fill=fill_colour))
                icon_x += cell_wid
                text_x += cell_wid
                #print(lob)
        d.save_svg(f'docs/{g}.svg')
        #d.save_png(f'docs/{g}.png')

    group_n = list(set(group_n))
    theme_n = list(set(theme_n))


def special_base(bases, name, features, connec_name, connec_dir):
    tob = BaseLocation(name,
                       {REGION: 'notingame', CUSTOMIZABLE: False, LOADING: False, INDOORS: False, FEATURES: features,
                        EXPLORED: False, CABINFEVERRISK: False}, colours=HEXES)
    conn = BaseConnection(connec_name, connec_dir, 'bottom,left', name, 'top,left', 'todo')
    bases[connec_name].add_connection(conn)
    tob.add_connection(conn)
    bases[name] = tob
    return tob


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        print('Drawing', fname)
        if fname.endswith('.json'):
            outfile = fname.replace('.json', '.svg')
            bases, colours = process_input(fname)
            # TODO automatically centre the base system rather than manually specifying
            draw_bases(bases, colours, output=outfile, width=2700, height=1800, base_x=2160, base_y=140, print_output=False)

    else:
        doctest.testmod()
        print('To run: python3 TLDBaseViz.py mybases.json')