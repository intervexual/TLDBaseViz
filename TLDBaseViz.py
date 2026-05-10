from keysAndDefs import *

class Region:
    def __init__(self, name,
                 width, height, x_offset, y_offset,
                 canvas_width, canvas_height,
                 region_json, regions_seen,
                 margin=10):
        self.name = name
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.region_json = region_json

        assert 'top' in region_json or 'bottom' in region_json, name

        if 'top' in region_json:
            if not '~' in region_json['top']:
                self.top = int(region_json['top'])
            else:
                top_key = region_json['top'].split('~')[1]
                direction = region_json['top'].split('~')[0]
                assert direction in ['top', 'bottom']
                if direction == 'bottom':
                    self.top = regions_seen[top_key].bottom
                else:
                    self.top = regions_seen[top_key].top
        elif 'bottom' in region_json:
            top_key = region_json['bottom'].split('~')[1]
            direction = region_json['bottom'].split('~')[0]
            assert direction in ['top', 'bottom']
            if direction == 'bottom':
                self.bottom = regions_seen[top_key].bottom
            else:
                self.bottom = regions_seen[top_key].top
            self.top = self.bottom - height

        self.bottom = self.top + height

        # TEMP
        self.left = 0# 1000*len(regions_seen)
        self.right = 0

    def update_horizontal(self, regions_seen):
        if 'right' in self.region_json:
            if not '~' in self.region_json['right']:
                self.right = self.canvas_width
                #print('END at', self.name)
            else:
                direction = self.region_json['right'].split('~')[0]
                right_key = self.region_json['right'].split('~')[1]
                if direction == 'left':
                    self.right = regions_seen[right_key].left
                else:
                    self.right = regions_seen[right_key].right
            self.left = self.right - self.width
        else:
            direction = self.region_json['left'].split('~')[0]
            right_key = self.region_json['left'].split('~')[1]
            if direction == 'left':
                self.left = regions_seen[right_key].left
            else:
                self.left = regions_seen[right_key].right
            self.right = self.left + self.width

    def draw(self, d):
        rect = draw.Rectangle( self.left, self.top,
                              self.width, self.height,
                              stroke='blue', stroke_width=5,
                              fill='white',opacity=0.5)
        d.append(rect)
        mid_x = self.left + self.width / 2
        mid_y = self.top + self.height / 2
        d.append(draw.Text(self.name, 40, mid_x, mid_y))


class BaseFeature:
    def __init__(self, name, colours=(), probability=1, qty=1):
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
        >>> str(BaseFeature('chest'))
        'chest:actual:base'
        >>> str(BaseFeature('*chest'))
        Traceback (most recent call last):
        ...
        AssertionError: *chest is not craftable
        >>> str(BaseFeature('!transmitter'))
        'transmitter:actual:prepare'
        """
        self.qty = float(qty)
        if QTY_MARKER in name and not name.startswith(TOTEXT):
            qty_info = name.split(QTY_MARKER)
            name = qty_info[0]
            self.qty = float(qty_info[1])

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
                assert not TODO_TYPES[self.name] in [BRING, TOBRING], f'{name} is not craftable'
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
        elif self.qty != 1:
            scaling = .6
            new_wid = wid*scaling
            diff = hei - new_wid
            new_y = y + (diff)
            import_svg(g, self.filepath, x=x, y=new_y, wid=new_wid,
                   hei=new_wid, fill=self.hex, opacity=self.probability)
            tbox_wid = new_wid * scaling
            g.append(draw.Rectangle(x+wid/2, y, tbox_wid, tbox_wid, fill=self.hex, opacity=.3))
            g.append(draw.Text( str(int(self.qty)), tbox_wid*.8,
                               x = x+wid-tbox_wid*.9, y=y+tbox_wid*.75,
                                text_anchor='middle'))
        else:
            import_svg(g, self.filepath, x=x, y=y, wid=wid,
                   hei=hei, fill=self.hex, opacity=self.probability) # shading for probabalistic features

class BaseConnection:
    def __init__(self,
                 source, direction, source_corner,
                 sink, sink_corner, kind, colours=False):
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
    def coord_based_direction(self, bases):
        """
        Redo the corner/connections based on coordinates
        :param source_ob:
        :param sink_ob:
        :return:
        >>> source_info = 'mybases.json'
        >>> b, e, regions = parse_input(source_info)
        >>> b, c = process_input(source_info)
        >>> these_bases = bases_of_region(b, 'CoastalHighway')
        >>> total_x, total_y, x_offset, y_offset = region_size_from_coords(these_bases, margin=100)
        >>> type(x_offset)
        <class 'int'>
        >>> m = calculate_region_coords(b, regions, 'CoastalHighway', total_x, total_y, x_offset, y_offset)
        >>> bob = BaseConnection("QuonsetGarage", "east", "top,left", "AbandonedMine(Lower)", "top,right", "path")
        >>> b[bob.source].region_coords
        [2100, 800]
        >>> b[bob.sink].region_coords
        [1300, 400]
        >>> bob.direction
        'east'
        >>> ang = bob.coord_based_direction(b) # should be > 270 and < 350
        >>> ang > 270 and ang < 350
        True
        >>> bob.direction
        'west'
        >>> bob = BaseConnection("QuonsetGarage", "east", "top,left", "FishHut(Eastmost)", "top,right", "path")
        >>> bob.direction
        'east'
        >>> ang = bob.coord_based_direction(b) # should be > 90 and < 270
        >>> ang > 90 and ang < 270
        True
        >>> bob.direction # expecting south
        'south'
        >>> bob.corners['QuonsetGarage']
        >>> bob.corners['FishHut(Eastmost)']
        """
        source_ob = bases[self.source]
        sink_ob = bases[self.sink]

        angle = angle_between( source_ob.region_coords, sink_ob.region_coords )
        vert, horiz, dir = direction_and_anchor(angle)
        vert, horiz, dir = direction_and_anchor_tiebreaking(vert, horiz, dir)

        self.corners[self.source] = f'{vert},{horiz}'
        self.direction = dir
        self.reverse = REVERSE[dir]

        # TODO how to handle the corner of the sink?
        rev_angle = angle_between(  sink_ob.region_coords, source_ob.region_coords )
        vert, horiz, dir = direction_and_anchor(rev_angle)
        vert, horiz, dir = direction_and_anchor_tiebreaking(vert, horiz, dir)
        self.corners[self.sink] = f'{vert},{horiz}'

        return angle

    def invert(self, colours):
        return BaseConnection(self.sink, self.reverse, self.sink_corner, self.source, self.source_corner, self.kind, colours)
    def __repr__(self):
        """
        Textual representation of the connection
        :return: representation as string
        >>> b, e, r = parse_input('tests/testinput.json')
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
        >>> b, e, r = parse_input('tests/testinput.json')
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
        [saltdeposit:actual:base, beachcombing:actual:base]
        [bed:actual:base, trader:actual:base, quality:actual:base]
        [builtworkbench:planned:cedar, furnbench:planned:cedar, bearbed:planned:fir]
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
        self.coords = ["",""]
        self.region_coords = ["",""]
        if COORDS in data:
            self.coords = data[COORDS]
        if self.loading:
            if REGION_CONNECTOR not in self.name:
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

        self.unused = []
        if 'unused' in data:
            self.unused += data['unused']
        self.removed = []
        if 'removed' in data:
            self.removed = data['removed']

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

        # manually position the current inventory
        if self.region == INVENTORY:
            self.box_x = self.cell_size
            self.box_y = self.cell_size + 2050
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
                        unexplored=HEXES[UNEXPLORED], border=HEXES[BASE], fill=HEXES[BASE_BG]):
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
                neighbour.draw(d, self.icon_size, x=neigh_left, y=neigh_top, unexplored=unexplored, border=border, fill=fill)
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
    >>> status_from_prefixes('chest')
    ('actual', 'base')
    >>> status_from_prefixes('+chest')
    ('planned', 'bring')
    >>> status_from_prefixes('*chest') # isn't actually makeable
    ('planned', 'make')
    >>> status_from_prefixes('$plastic')
    ('actual', 'moved-customization')
    >>> status_from_prefixes('$workbench')
    ('actual', 'moved-customization')
    >>> status_from_prefixes('!transmitter')
    ('actual', 'prepare')
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
    elif s.startswith(GLITCHBROUGHT):
        return ACTUAL, MOVED
    elif s.startswith(TOPREPARE):
        return ACTUAL, PREPARE

    return ACTUAL, BASE


def parse_input(filename='bases.json', regionfile='regions.json'):
    """
    Load JSON into dictionary format
    :param filename: input filename
    :return: dictionaries for base info & colour scheme
    >>> b, e, r = parse_input('tests/testinput.json')
    >>> b['Quonset']['indoors']
    True
    >>> b['Quonset']['region']
    'CoastalHighway'
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    bases = data[BASES]
    edges = data[CONNECTIONS]
    regions = {}
    if REGIONS in data:
        regions = data[REGIONS]
    else:
        with open(regionfile, 'r') as f:
            regions = json.load(f)
    return bases, edges, regions


def parse_edges(edges, colours=False):
    """
    Convert the lists of edges from the JSON into BaseConnection objects.
    :return: dictionary, indexed by base names, each with a list of BaseConnection objects that go to/from the base.
    >>> b, e, r = parse_input('tests/testinput.json')
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


def add_base(b, base_info, base_objects, colours, edges, to_print=False):
    bob = BaseLocation(b, base_info, colours)
    if b in edges:
        for connection_to_b in edges[b]:
            bob.add_connection(edges[b][connection_to_b])
    base_objects[b] = bob
    if to_print:
        print(bob)

def process_input(filename='bases.json', to_print=False, style_file='styling.json'):
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
    [saltdeposit:actual:base, beachcombing:actual:base]
    [bed:actual:base, trader:actual:base, quality:actual:base]
    [builtworkbench:planned:cedar, furnbench:planned:cedar, bearbed:planned:fir]
    ---
    >>> bases.keys()
    dict_keys(['UpperMine', 'LowerMine', 'Quonset', 'QMFishHut', 'Misanthrope', 'JMFishHut', 'Jackrabbit', 'JFFishHut', 'MidFishHuts', 'CommuterCar', 'Harris', 'No3Mine', 'No5Mine', 'Hibernia', 'LonelyLighthouse', 'BrokenBridge', 'Riken', 'LittleIsland', 'MTFarm'])
    >>> bases, colours = process_input('mybases.json')
    >>> #bases
    """
    bases, edges, regions = parse_input(filename)
    if style_file == STYLE_FILE:
        colours = HEXES
    else:
        raw_colours, DASHSTYLE, FILLS, STROKES = parse_styling(style_file)
        colours = parse_colours(raw_colours)

    edges = parse_edges(edges, colours)
    if len(edges) == 0:
        print('No edges! Old system!')
    base_objects = {}
    for b in bases:
        if not b.startswith(COMMENT):
            add_base(b, bases[b], base_objects, colours, edges, to_print=to_print)
        else:
            for k in bases[b]:
                add_base(k, bases[b][k], base_objects, colours, edges, to_print=to_print)
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
               add_legend=True, output_png=True, print_output=False, print_warnings=True):
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

    last_base_name = ''
    for b in bases:
        last_base_name = b
        if print_output:
            print('Visiting', b)
        arrow_size = icon_size
        #print('\n', b, '*'*35)
        bob = bases[b]
        w, h, c, m = bob.box_dimensions(icon_size)
        if not bob.is_drawn:
            g = draw.Group(id=b)
            bob.draw(g, icon_size, x=base_x, y=base_y,
                     unexplored=unexplored_colour, border=colours[BASE], fill=colours[BASE_BG])
            gb.append(g)
            if print_output:
                print(' '*TABSIZE + 'Drawing', b)
            visited.append(b)

        # then the neighbours
        for connection_name in bob.connections:
            if connection_name in bases:
                dir = bob.connections[connection_name]
                bases[b].draw_connection(gb, bases[connection_name],
                                         unexplored=unexplored_colour, border=colours[BASE], fill=colours[BASE_BG],
                                         print_output=print_output)
            elif print_warnings:
                print('Warning: connected base not in bases', connection_name)

    d.append(gb)
    #d.append(draw.Use(gb, 0, 0))

    counts = {}
    if add_legend: # count before the special bases are added
        counts = count_features(bases)

    if CURR_INVENTORY in bases:
        last_base_name = USED_UP
    to_bring, to_take = verify_taking_numbers(bases)
    out_bring = 'outstanding bring (needs source)'
    out_take = 'outstanding take (needs destination)'
    to_bring = condense_multiples_in_list(to_bring)
    to_take = condense_multiples_in_list(to_take)
    bob = special_base(bases, out_bring, to_bring, last_base_name, SOUTH, colours=colours)
    tob = special_base(bases, out_take, to_take, out_bring, SOUTH, colours=colours)
    bases[last_base_name].draw_connection(d, bob,
                                          unexplored=colours[TAKE],
                                          border=colours[TAKE],
                                          fill=colours[BASE_BG])
    bases[out_bring].draw_connection(d, tob,
                                     unexplored=colours[BRING],
                                     border=colours[BRING],
                                     fill=colours[BASE_BG])

    if add_legend:
        first_col_break = 65
        second_col_break = first_col_break
        draw_legend(d, colours, x=d.width-210*3-40, y=880,
                    counts=counts,
                    column_breaks=(first_col_break, first_col_break + second_col_break))


    d.save_svg(output)
    if output_png:
        d.save_png(output.replace('.svg','.png'))


def get_regions(bases):
    """
    Get unique regions from the bases
    :return: list of regions
    >>> bases, edges = process_input('tests/testinput.json')
    >>> get_regions(bases)
    ['CoastalHighway', 'DesolationPoint', 'MountainTown', 'OIC']
    >>> bases, edges = process_input('templates/loot4.json')
    >>> get_regions(bases)
    ['AshCanyon', 'Blackrock', 'BleakInlet', 'BrokenRailroad', 'CoastalHighway', 'DesolationPoint', 'FarRangeBranchLine', 'ForlornMuskeg', 'ForsakenAirfield', 'HushedRiverValley', 'KPN', 'KPS', 'MountainTown', 'MysteryLake', 'OIC', 'PleasantValley', 'Ravine', 'SunderedPass', 'TimberwolfMountain', 'TransferPass', 'WindingRiver', 'ZoneOfContamination']
    """
    regions = []
    to_exclude = [USED_UP, INVENTORY, 'NotInGame', CURR_INVENTORY]
    for b in bases:
        this_region = bases[b].region
        if this_region not in to_exclude:
            regions.append(this_region)
    return sorted(list(set(regions)))


def bases_of_region(bases, region):
    """
    Filter bases to just those from a region.
    :param bases: dict of bases {str: BaseLocation}
    :param region: region name as string, e.g. 'AshCanyon'
    :return: dict of bases from that region, {str: BaseLocation}
    >>> source_info = 'mybases.json'
    >>> bases, colours = process_input(source_info)
    >>> these_bases = bases_of_region(bases, 'MysteryLake')
    >>> 'CampOffice' in these_bases.keys()
    True
    >>> twm = bases_of_region(bases, 'TimberwolfMountain')
    >>> 'Cave(Summit)' in twm.keys()
    True
    >>> type(twm['PrepperCache(TWM)'])
    <class '__main__.BaseLocation'>
    >>> farterr = bases_of_region(bases, ['SunderedPass', 'ForsakenAirfield', 'ZoneOfContamination', 'TransferPass'])
    >>> 'IdleCamp' in farterr.keys() and 'MainHangar' in farterr.keys() and 'VacantDepot' in farterr.keys() and 'LastLonelyHouse' in farterr.keys()
    True
    >>> type(farterr['IdleCamp'])
    <class '__main__.BaseLocation'>
    """
    these_bases = {}
    for b in bases:
        bob = bases[b]
        if bob.region == region or bob.region in region:
            these_bases[b] = bob
    return these_bases


def draw_region(region, source_info, output='tests/',
                print_output=False, add_legend=True):
    """
    Draw only the bases of one region.
    :param region: region name as string, e.g. 'AshCanyon'
    :param source_info: input json filename
    :return:
    >>> draw_region('AshCanyon', 'templates/loot4.json', print_output=False)
    >>> draw_region('TimberwolfMountain', 'templates/loot4.json', print_output=False, add_legend=True)
    >>> draw_region('Blackrock', 'mybases.json', print_output=False)
    >>> draw_region('PleasantValley', 'mybases.json', print_output=False)
    >>> draw_region('MountainTown', 'mybases.json', print_output=False)
    >>> draw_region('MysteryLake', 'templates/loot4.json', print_output=False)
    >>> draw_region('ForlornMuskeg', 'templates/loot4.json', print_output=False)
    >>> draw_region('SunderedPass', 'templates/loot4.json', print_output=False)
    >>> draw_region('HushedRiverValley', 'templates/loot4.json', print_output=False, add_legend=True)
    """
    bases, colours = process_input(source_info)
    these_bases = bases_of_region(bases, region)

    output = output + region + '.svg'

    draw_bases(these_bases, colours,
               base_x = 1500, base_y = 1500,
               width = 2500, height = 2500,
               add_legend=add_legend, print_output=print_output,
               output=output, output_png=False, print_warnings=False)


def region_size_from_coords(these_bases,
                            use_region=False,
                            margin=100):
    """
    Using coordinates, calculate the size of a region using the same units
    :param these_bases: dict of {str: BaseLocation}, where all bases are in a given region
    :param margin: additional units of space to add to margins of imaginary rectangle around the bases
    :return: width, height, x_offset, y_offset
    >>> source_info = 'mybases.json'
    >>> b, e, regions = parse_input(source_info)
    >>> bases, colours = process_input(source_info)
    >>> region_size_from_coords(bases_of_region(bases, 'MysteryLake'))
    (1900, 1800, 100, 300)
    >>> region_size_from_coords(bases_of_region(bases, 'ForsakenAirfield'))
    (2600, 2600, -1000, 1400)
    >>> region_size_from_coords(bases_of_region(bases, 'Ravine'))
    (1300, 500, -1000, 400)
    """
    max_x, max_y = 0, 0
    min_x, min_y = 50000, 50000

    # max and min coords
    for b in these_bases:
        bob = these_bases[b]
        if use_region:
            x = bob.region_coords[0]
            y = bob.region_coords[1]
        else:
            x = bob.coords[0]
            y = bob.coords[1]
        assert type(x) in [int,float] and type(y) in [int,float], f'{b}: {x}, {y}'
        max_x = max(x, max_x)
        max_y = max(y, max_y)
        min_x = min(x, min_x)
        min_y = min(y, min_y)
        #print(b, x, y)

    total_x = (max_x - min_x) + margin*2
    total_y = (max_y - min_y) + margin*2
    x_offset = min_x + margin
    y_offset = -min_y + margin

    return total_x, total_y, x_offset, y_offset


def rotate_point_wrt_center(point_to_be_rotated, angle, center_point=(0, 0)):
    """
    Rotate clockwise around a point. This code was shared by somebody named Leon
    on StackExchange: https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
    and I added the doctests.
    :param point_to_be_rotated:
    :param angle:
    :param center_point:
    :return:
    >>> rotate_point_wrt_center((10, 0), 90, (10, 10))
    (20.0, 10.0)
    >>> rotate_point_wrt_center((10, 0), -90, (10, 10))
    (0.0, 10.0)
    >>> rotate_point_wrt_center((10, 0), 180, (10, 10))
    (10.0, 20.0)
    >>> rotate_point_wrt_center((10, 0), 360, (10, 10))
    (10.0, 0.0)
    """
    angle = math.radians(angle)

    xnew = math.cos(angle) * (point_to_be_rotated[0] - center_point[0]) - math.sin(angle) * (
                point_to_be_rotated[1] - center_point[1]) + center_point[0]
    ynew = math.sin(angle) * (point_to_be_rotated[0] - center_point[0]) + math.cos(angle) * (
                point_to_be_rotated[1] - center_point[1]) + center_point[1]

    return (round(xnew, 2), round(ynew, 2))


def angle_between(p1, p2):
    """
    Angle between the imaginary upward line from p1
    and the imaginary outward line from p1 to p2.
    :param p1: (x,y)
    :param p2: (x,y)
    :return:
    >>> angle_between( [10, 10], [10,0] ) # north
    0.0
    >>> angle_between( [10, 10], [10,20]  ) # south
    180.0
    >>> angle_between( [10, 10], [20,10] ) # east
    90.0
    >>> angle_between( [10, 10], [0,10] ) # west
    270.0
    >>> angle_between( [10, 10], [0,0]) # 45 deg
    315.0
    >>> angle_between( [0,0], [10,10] ) # 180 from prev
    135.0
    >>> angle_between( [10,10], [20,20] )
    135.0
    >>> angle_between( [800,600], [0,1000])
    243.434948822922
    >>> angle_between(  [0,1000], [800,600])
    63.43494882292201
    """
    theta = math.atan2((p2[1] - p1[1]), (p2[0] - p1[0]))
    return (math.degrees(theta) + 90) % 360


def direction_and_anchor(angle):
    """

    :return:
    >>> direction_and_anchor(0) # must be north and top, could be left or right
    ('top', 'leftright', 'north')
    >>> direction_and_anchor(180) # must be south and bottom, could be left or right
    ('bottom', 'leftright', 'south')
    >>> direction_and_anchor(90) # must be right and east, could be top or bottom
    ('topbottom', 'right', 'east')
    >>> direction_and_anchor(270) # must be left and west, could be top or bottom
    ('topbottom', 'left', 'west')
    >>> direction_and_anchor(45) # (top,right), could be north or east
    ('top', 'right', 'northeast')
    >>> direction_and_anchor(45+90)
    ('bottom', 'right', 'southeast')
    >>> direction_and_anchor(45+180)
    ('bottom', 'left', 'southwest')
    >>> direction_and_anchor(45+90+180)
    ('top', 'left', 'northwest')
    >>> direction_and_anchor(40)
    ('top', 'right', 'north')
    >>> direction_and_anchor(50)
    ('top', 'right', 'east')
    >>> direction_and_anchor(40+90)
    ('bottom', 'right', 'east')
    >>> direction_and_anchor(50+90)
    ('bottom', 'right', 'south')
    >>> direction_and_anchor(-20)
    ('top', 'left', 'north')
    """
    angle = angle % 360
    vert_anchor = ''
    horiz_anchor = ''
    direction = ''

    if angle <= 90 or angle >= 270:
        vert_anchor += "top"
    if angle >= 90 and angle <= 270:
        vert_anchor += "bottom"

    if angle >= 180 or angle <= 0:
        horiz_anchor += "left"
    if angle >= 0 and angle <= 180:
        horiz_anchor += "right"

    if angle <= 45 or angle >= 45+270:
        direction += 'north'
    if angle >= 45+90 and angle <= 45+180:
        direction += "south"
    if angle >= 45 and angle <= 45+90:
        direction += "east"
    if angle >= 45+180 and angle <= 45+270:
        direction += 'west'

    return vert_anchor, horiz_anchor, direction


def direction_and_anchor_tiebreaking(vert, horiz, dir):
    # TODO better tie breaking
    if vert == 'leftright':
        vert = 'left'
    if horiz == 'topbottom':
        horiz = 'top'
    if 'north' in dir:
        dir = 'north'
    if 'south' in dir:
        dir = 'south'
    return vert, horiz, dir


def calculate_region_coords(these_bases, regions, region,
                            total_x, total_y, x_offset, y_offset,
                            margin=100):
    """

    :param these_bases:
    :param regions:
    :param unit_size:
    :return:
    >>> source_info = 'mybases.json'
    >>> b, e, regions = parse_input(source_info)
    >>> bases, colours = process_input(source_info)
    >>> region = 'MysteryLake'
    >>> these_bases = bases_of_region(bases, region)
    >>> total_x, total_y, x_offset, y_offset = region_size_from_coords(these_bases, margin=100)
    >>> calculate_region_coords(these_bases, regions, region, total_x, total_y, x_offset, y_offset)
    (1800.0, 1900.0)
    >>> these_bases['CampOffice'].region_coords # [1100, 1000] before rotation
    [800.0, 1100.0]
    >>> these_bases['TrappersHomestead'].region_coords  # [100, 1500] before rotation
    [300.0, 100.0]
    """
    mid_x = total_x/2
    mid_y = total_y/2

    for b in these_bases:
        bob = these_bases[b]
        if bob.region in regions:
            if regions[region][X_MIRRORING]:
                assert type(bob.coords[0]) in [int, float], bob
                assert type(x_offset) in [int, float], bob
                assert type(margin) in [int, float], bob
                x = total_x - (bob.coords[0] - x_offset) - margin*2
            else:
                assert type(bob.coords[0]) in [int, float], bob
                assert type(x_offset) in [int, float], bob
                assert type(margin) in [int, float], bob
                x = bob.coords[0] - x_offset + margin*2
            if regions[region][Y_MIRRORING]:
                y = bob.coords[1] + y_offset
            else:
                y = total_y - (bob.coords[1] + y_offset) # Y axis in maps goes opposite direction than canvas, unless it's PV
            # rotate point if whole region is rotated
            if regions[bob.region]['rotation'] != 0:
                rotate_cw = regions[bob.region]['rotation']
                x, y = rotate_point_wrt_center((x,y), -rotate_cw, (mid_x, mid_y))

            bob.region_coords = [x, y]

    # rotated regions need new dimensions
    if bob.region in regions and regions[bob.region]['rotation'] != 0:
        total_x, total_y, x_offset, y_offset = region_size_from_coords(these_bases,
                                                                       use_region=True,
                                                                       margin=margin)
        for b in these_bases:
            bob = these_bases[b]
            bob.region_coords[0] -= x_offset
            bob.region_coords[0] += 2*margin
            bob.region_coords[1] += y_offset

    return total_x, total_y


def draw_just_region_from_coords(d, these_bases,
                                 total_x, total_y,
                                 unit_size=10):
    """
    Add the bases in these_bases to the Drawing canvas but don't save it yet
    :param d: Drawing object
    :param these_bases: dict of {str: BaseLocation}, where all bases are in a given region
    :param total_x: width of the region
    :param total_y: height of the region
    :param unit_size: used for spacing out text
    :return:
    """
    d.append(draw.Rectangle(0, 0, total_x, total_y,
                            fill='white', stroke='blue', stroke_width=unit_size/2))
    drawn = []
    for b in these_bases:
        bob = these_bases[b]
        x, y = bob.region_coords
        #print(b, x, y)
        circ_fill = 'black'
        if REGION_CONNECTOR in b:
            circ_fill = 'red'
        d.append(draw.Circle(x, y, unit_size, fill=circ_fill))
        d.append(draw.Text(b, 3*unit_size, x, y, fill=circ_fill))
        drawn.append(b)
        # draw connections?
        for c in bob.connections:
            if c in drawn:
                #print('\tdrawing', b, c)
                #p = draw.Path(stroke='blue', stroke_width=unit_size/5)
                cob = bob.edges[c]
                p = draw.Path(stroke_width=unit_size/2, stroke=cob.colour, stroke_dasharray=cob.dasharray)

                p.M(x, y)
                p.L(*these_bases[c].region_coords)
                d.append(p)


def add_region_connections(region, regions, bases, these_bases):
    for connec in regions[region]["connections"]:
        connec_reg = connec[0]
        connec_x = connec[1]
        connec_y = connec[2]
        connec_name = f'{region}{REGION_CONNECTOR}{connec_reg}'
        data = {'name': connec_name,
                REGION: region,
                CUSTOMIZABLE: False,
                INDOORS: False,
                EXPLORED: True,
                LOADING: True,
                CABINFEVERRISK: False,
                COORDS:[connec_x, connec_y],
                FEATURES: []
                }
        bob = BaseLocation(connec_name, data)
        bases[connec_name] = bob
        these_bases[connec_name] = bob

def draw_region_coords(region, source_info, output='tests/', print_output=False, add_legend=False):
    """
    Draw only the bases of one region.
    :param region: region name as string, e.g. 'AshCanyon'
    :param source_info: input json filename
    :return:
    >>> draw_region_coords('MysteryLake', 'mybases.json', print_output=False)
    >>> draw_region_coords('MountainTown', 'mybases.json', print_output=False)
    >>> draw_region_coords('Ravine', 'mybases.json', print_output=False)
    >>> draw_region_coords('HushedRiverValley', 'mybases.json', print_output=False)
    >>> draw_region_coords('PleasantValley', 'mybases.json', print_output=False)
    >>> draw_region_coords('TimberwolfMountain', 'mybases.json', print_output=False)
    >>> draw_region_coords('Blackrock', 'mybases.json', print_output=False)
    >>> draw_region_coords('AshCanyon', 'mybases.json', print_output=False)
    >>> draw_region_coords('BleakInlet', 'mybases.json', print_output=False)
    >>> draw_region_coords('BrokenRailroad', 'mybases.json', print_output=False)
    >>> draw_region_coords('CoastalHighway', 'mybases.json', print_output=False)
    >>> draw_region_coords('OIC', 'mybases.json', print_output=False)
    >>> draw_region_coords('DesolationPoint', 'mybases.json', print_output=False)
    >>> draw_region_coords('FarRangeBranchLine', 'mybases.json', print_output=False)
    >>> draw_region_coords('ForlornMuskeg', 'mybases.json', print_output=False)
    >>> draw_region_coords('TransferPass', 'mybases.json', print_output=False)
    >>> draw_region_coords('KeepersPass', 'mybases.json', print_output=False)
    >>> draw_region_coords('WindingRiver', 'mybases.json', print_output=False)
    >>> draw_region_coords('ForsakenAirfield', 'mybases.json', print_output=False)
    >>> draw_region_coords('SunderedPass', 'mybases.json', print_output=False)
    >>> draw_region_coords('ZoneOfContamination', 'mybases.json', print_output=False)
   """
    b, e, regions = parse_input(source_info)
    bases, colours = process_input(source_info)
    these_bases = bases_of_region(bases, region)
    add_region_connections(region, regions, bases, these_bases)

    output = output + 'coords_' + region + '.svg'

    margin = 50
    total_x, total_y, x_offset, y_offset = region_size_from_coords(these_bases, margin=margin)
    total_x, total_y = calculate_region_coords(these_bases, regions, region, total_x, total_y, x_offset, y_offset, margin=margin)

    unit_size = 10

    d = draw.Drawing(total_x, total_y)

    draw_just_region_from_coords(d, these_bases, total_x, total_y, unit_size)
    d.save_svg(output)


def draw_multiple_regions_from_coords(these_regions, source_info,
                                      output='tests/' ):
    """
    :param regions:
    :param source_info:
    :param output:
    :return:
    # 'HushedRiverValley','MountainTown','ForlornMuskeg','BleakInlet', 'OIC','DesolationPoint'
    >>> draw_multiple_regions_from_coords(['AshCanyon', 'TimberwolfMountain', 'PleasantValley', 'CoastalHighway'], 'mybases.json')
    >>> draw_multiple_regions_from_coords([], 'mybases.json')
    """
    b, e, regions = parse_input(source_info)
    bases, colours = process_input(source_info)

    output = output + f'coords_map{len(these_regions)}.svg'

    margin = 50
    unit_size = 10
    canvas_width = 12000
    canvas_height = 9000
    d = draw.Drawing(canvas_width, canvas_height)

    coords = {}

    # first figure out all region Ys
    y_ordered = ['AshCanyon','TimberwolfMountain',
                 'PleasantValley',
                 'CoastalHighway','OIC','DesolationPoint',
                 'Blackrock','KeepersPass',
                 'WindingRiver','Ravine',
                 'MysteryLake',
                 'ForlornMuskeg','MountainTown','HushedRiverValley',
                 'BleakInlet',
                 'BrokenRailroad',
                 'ZoneOfContamination',
                 'TransferPass',
                 'FarRangeBranchLine',
                 'ForsakenAirfield','SunderedPass']
    if len(these_regions) == 0:
        these_regions = y_ordered
    for region in y_ordered:
        these_bases = bases_of_region(bases, region)
        total_x, total_y, x_offset, y_offset = region_size_from_coords(these_bases, margin=margin)
        calculate_region_coords(these_bases, regions, region, total_x, total_y, x_offset, y_offset, margin=margin)

        #print(region, regions[region])
        #print(coords.keys())
        coords[region] = Region(region,
                        total_x, total_y, x_offset, y_offset,
                        canvas_width, canvas_height,
                        regions[region], coords)

    left_to_right = ['DesolationPoint', 'OIC', 'CoastalHighway',
                     'PleasantValley',
                     'Ravine', 'KeepersPass',
                     'MysteryLake','ForlornMuskeg',
                     'BrokenRailroad',
                     'FarRangeBranchLine', 'TransferPass',
                     'ForsakenAirfield', 'SunderedPass',
                     'ZoneOfContamination',
                     'MountainTown','HushedRiverValley',
                     'BleakInlet',
                     'WindingRiver',
                     'TimberwolfMountain','AshCanyon',
                     'Blackrock']
    # then figure out all region Xs
    for region in left_to_right:
        coords[region].update_horizontal(coords)

    for region in these_regions:
        coords[region].draw(d)
        #draw_just_region_from_coords(d, these_bases, total_x, total_y, unit_size)
    d.save_svg(output)


def count_features(bases,
                   statuses_to_count=(ACTUAL, REMOVE, FIND),
                   materials_to_count=(FIND, REMOVE),
                   do_not_count=(BRING, TOBRING)):
    """
    For each feature (e.g. workbench, forge) count how many times it appears across the whole island.
    :param bases: list of BaseLocation objects
    :return: dictionary of counts, indexed by feature name (e.g. 'forge')
    >>> bases, colours = process_input('tests/testinput.json')
    >>> type(count_features(bases))
    <class 'dict'>
    >>> bases, colours = process_input('mybases.json')
    >>> nums = count_features(bases)
    >>> [nums['forge'], nums['milling'], nums['radio'], nums['trader'], nums['saltdeposit'], nums['range'], nums['woodworking']] # fixed for any given sandbox
    [4.0, 2.0, 10.0, 1.0, 14.0, 7.0, 4.0]
    >>> #pv = bases_of_region(bases, 'PleasantValley')
    >>> #count_features(pv)['prybar'] # 0
    >>> #pv['Barn(Archery)'].features[0][-1] # planned bring
    """
    count = {}
    for a in ASSETS:
        count[a] = 0

    for b in bases:
        for row in bases[b].features:
            for feature in row:
                if feature.material in do_not_count or feature.status in do_not_count:
                    #print(feature.material, feature.status)
                    pass
                else:
                    to_count_mat = feature.material in materials_to_count
                    to_count_stat = feature.status in statuses_to_count
                    if to_count_mat or to_count_stat:
                        count[feature.name] += feature.probability * feature.qty
    return count


def verify_fixed_numbers(bases, nums):
    """

    :param bases:
    :return:
    >>> bases, colours = process_input('templates/loot4.json')
    >>> nums = count_features(bases)
    >>> verify_fixed_numbers(bases, nums)
    >>> bases, colours = process_input('mybases.json')
    >>> nums = count_features(bases)
    >>> verify_fixed_numbers(bases, nums)
    False
    """
    all_matching = True
    round_to = 2

    special_counts = {}
    special_sources = {}
    for i in ICONS:
        if i.fixedas != i.key:
            if i.fixedas not in special_counts:
                special_counts[i.fixedas] = 0
                special_sources[i.fixedas] = []
            special_counts[i.fixedas] += round(nums[i.key],round_to)
            special_sources[i.fixedas].append(i.key)

    for i in ICONS:
        if type(i.fixednum) == float:
            if round(i.fixednum,round_to) != round(nums[i.key],round_to):
                all_matching = False
                if i.key in special_counts:
                    total = special_counts[i.key] + nums[i.key]
                    if round(i.fixednum,round_to) != round(total,round_to):
                        print('Warning: expecting', i.fixednum, 'many', i.key, f'including ({special_sources[i.key]})', 'found', total, 'instead')
                else:
                    print('Warning: expecting', i.fixednum, 'many', i.key, 'found', nums[i.key], 'instead')

    return all_matching


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
    to_take = count_features(bases, statuses_to_count=[TAKE], materials_to_count=[TAKE])
    to_bring = count_features(bases, statuses_to_count=[BRING], materials_to_count=[BRING], do_not_count=[])
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

                to_add = ','.join(abs(math.ceil(round(diff,3))) * [posn + a])
                if diff > 0:
                    unknown_take += [to_add]
                else:
                    unknown_bring += [to_add]

    return unknown_take, unknown_bring


def condense_multiples_in_list(lst):
    """

    :param lst:
    :return:
    >>> condense_multiples_in_list(['-maglens', '-lantern', '-stim', '-cedar,-cedar,-cedar,-cedar,-cedar,-cedar,-cedar,-cedar,-cedar,-cedar,-cedar,-cedar,-cedar', '-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir,-fir', '-deerhide'])
    ['-maglens,-lantern,-stim,-cedar:13,-fir:52,-deerhide']
    """
    freqs = {}
    for entry in lst:
        indivs = entry.split(',')
        for item in indivs:
            if item not in freqs:
                freqs[item] = 1
            else:
                freqs[item] += 1
    condensed = []
    for key in freqs:
        if freqs[key] > 1:
            s = key + ':' + str(freqs[key])
            condensed.append(s)
        else:
            condensed.append(key)
    s = ','.join(condensed)
    condensed = [s]
    return condensed


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




def draw_legend(d, colours, x=0, y=0,
                icon_size=10, margin_ratio=1 / 8,
                legend_colour='purple', background_colour='white',
                column_breaks=(), counts=()):
    """
    Draw a legend
    :param d: drawing object
    :return: y position of the bottom of the legend
    >>> d = draw.Drawing(200, (36+12)*25)
    >>> d.append(draw.Rectangle(0, 0, d.width, d.height, fill='white'))
    >>> bases, colours = process_input('mybases.json')
    >>> draw_legend(d, colours, icon_size=20) > 1000
    True
    >>> d.save_svg('tests/legend.svg')
    """
    margin_size = icon_size * margin_ratio
    cell_size = icon_size + margin_size
    start_y = y + cell_size + margin_size * 2
    icon_y = start_y
    icon_x = x + margin_size
    g = draw.Group(id="legend")

    assert  len(ASSETS) - len(ORDERING) <= 1, len(ASSETS) - len(ORDERING)

    longest_name_len = 0
    for k in ORDERING:
        longest_name_len = max( len(ORDERING[k]), longest_name_len )

    legend_font_size = 10
    g.append(draw.Text('LEGEND', legend_font_size, font_family=FONTFAM,
                       x=icon_x, y=icon_y + cell_size / 2,
                       fill=legend_colour, stroke=legend_colour))
    text_wid = longest_name_len * (icon_size / 2) # + 1 * margin_size
    count_x = icon_x + text_wid

    lines_drawn = 0
    text_y = 0
    for i, a in enumerate(ORDERING):
        filepath = 'assets/' + ASSETS[a]

        to_draw = True
        if counts: # don't draw if there are none in the data
            if counts[a] == 0:
                to_draw = False

        if to_draw:
            if lines_drawn in column_breaks:
                icon_y = start_y
                legend_column_size = text_wid + cell_size * 5 + 4 * margin_size
                icon_x += legend_column_size
                count_x += legend_column_size

            icon_y += cell_size
            text_y = icon_y + cell_size / 2 + margin_size
            try:
                import_svg(g, filepath, x=icon_x, y=icon_y, wid=icon_size,
                           hei=icon_size, fill=legend_colour)
                lines_drawn += 1
            except:
                print('ERROR SVG import failed on', a, i)
            g.append(draw.Text(ORDERING[a], legend_font_size, font_family=FONTFAM,
                               x=icon_x+cell_size, y=text_y,
                               fill=legend_colour))
            if counts:
                count_num = round(counts[a], 2)
                if count_num == int(count_num):
                    count_num = int(count_num)
                count_txt = str(count_num)
                g.append(draw.Text(count_txt, legend_font_size, font_family=FONTFAM,
                                   x=count_x, y=text_y,
                                   fill=legend_colour))

    icon_y += cell_size
    text_y += cell_size
    import_svg(g, 'assets/bear.svg', x=icon_x, y=icon_y, wid=icon_size,
               hei=icon_size, fill=legend_colour, opacity=0.5)
    pb = 'opacity indicates probability (0.5 -> 50%)'
    g.append(draw.Text(pb, legend_font_size, font_family=FONTFAM,
                       x=icon_x + cell_size, y=text_y,
                       fill=legend_colour))

    colour_types = FILLS
    for j, a in enumerate(colour_types):
        icon_y += cell_size
        text_y += cell_size
        g.append(draw.Rectangle(fill=colours[a], x=icon_x, y=icon_y, width=icon_size, height=icon_size))
        g.append(draw.Text(colour_types[a], legend_font_size, font_family=FONTFAM,
                           x=icon_x+cell_size, y=text_y,
                           fill=legend_colour))

    path_types = STROKES
    for j, a in enumerate(path_types):
        icon_y += cell_size
        text_y += cell_size
        p = draw.Path(stroke=colours[a], stroke_width=margin_size, stroke_dasharray=DASHSTYLE[a] )
        p.M(icon_x, icon_y+cell_size/2)
        p.L(icon_x+icon_size, icon_y+cell_size/2)
        g.append(p)
        g.append(draw.Text(path_types[a], legend_font_size, font_family=FONTFAM,
                           x=icon_x+cell_size, y=text_y,
                           fill=legend_colour))

    icon_y += cell_size
    text_y += cell_size
    g.append(draw.Rectangle(fill='none', stroke=colours[BASE], x=icon_x, y=icon_y, width=icon_size, height=icon_size))
    g.append(draw.Text('customizable indoor location', legend_font_size, font_family=FONTFAM,
                       x=icon_x+cell_size, y=text_y,
                       fill=legend_colour))

    icon_y += cell_size
    text_y += cell_size
    g.append(draw.Rectangle(fill='none', stroke=colours[BASE], x=icon_x, y=icon_y, width=icon_size, height=icon_size, opacity=OUTDOOR_OPACITY))
    g.append(draw.Text('non-customizable indoor location', legend_font_size, font_family=FONTFAM,
                       x=icon_x+cell_size, y=text_y,
                       fill=legend_colour))


    icon_y += cell_size
    text_y += cell_size
    g.append(draw.Rectangle(fill='none', stroke=colours[BASE], x=icon_x, y=icon_y, width=icon_size, height=icon_size,
                            rx=icon_size/2.5, ry=icon_size/2.5, opacity=OUTDOOR_OPACITY))
    g.append(draw.Text('outdoors (cannot cure hides)', legend_font_size, font_family=FONTFAM,
                       x=icon_x+cell_size, y=text_y,
                       fill=legend_colour))

    icon_y += cell_size
    text_y += cell_size
    #d.append(draw.Rectangle(fill='none', stroke=colours[BASE], x=icon_x, y=icon_y, width=icon_size, height=icon_size, opacity=OUTDOOR_OPACITY))
    g.append(draw.Text('italics mean no loading screen', legend_font_size, font_family=FONTFAM,
                       x=icon_x+cell_size, y=text_y,
                       fill=legend_colour, font_style='italic'))

    d.append(g)
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


def special_base(bases, name, features, connec_name, connec_dir, colours=HEXES):
    tob = BaseLocation(name,
                       {REGION: NOTINGAME,
                        CUSTOMIZABLE: False, LOADING: False, INDOORS: False,
                        FEATURES: features,
                        EXPLORED: False, CABINFEVERRISK: False}, colours=colours)
    conn = BaseConnection(connec_name, connec_dir,
                          'bottom,left', name,
                          'top,left', 'fake', colours=colours)
    bases[connec_name].add_connection(conn)
    tob.add_connection(conn)
    bases[name] = tob
    return tob



def draw_bases_regionally_and_together(fname, region_folder='output/'):
    outfile = fname.replace('.json', '.svg')

    # TODO automatically centre the base system rather than manually specifying

    to_print = False
    if len(sys.argv) > 2 and '-v' in sys.argv[2:]:
        to_print = True
    style_file = STYLE_FILE
    if len(sys.argv) > 2 and '-s' in sys.argv[2:]:
        i = sys.argv.index('-s')
        style_file = sys.argv[i + 1]
        assert style_file.endswith('.json'), f'style file {style_file} should end with .json'

    bases, colours = process_input(fname, style_file=style_file)

    # verify the numbers BEFORE the special bases are added
    nums = count_features(bases)
    verify_fixed_numbers(bases, nums)

    draw_bases(bases, colours, output=outfile,
               width=4500, height=2500,
               base_x=3700, base_y=150,
               output_png=False, print_output=to_print)

    # by region

    regions = get_regions(bases)
    for r in regions:
        draw_region(r, fname, output=region_folder, print_output=False)

    super_regions = {
        'Northlands': ['PleasantValley', 'TimberwolfMountain', 'AshCanyon', 'KeepersPass', 'Blackrock', 'WindingRiver'],
        'FarTerritory': ['SunderedPass', 'ForsakenAirfield', 'ZoneOfContamination', 'TransferPass',
                         'FarRangeBranchLine'],
        # 'Miltonlands':['HushedRiverValley', 'MountainTown'],
        'Mainline': ['BrokenRailroad', 'ForlornMuskeg', 'MysteryLake', 'Ravine', 'CoastalHighway', 'OIC',
                     'DesolationPoint'],
        'Crossline': ['HushedRiverValley', 'MountainTown', 'ForlornMuskeg', 'BleakInlet'],
        # 'Coastline':['DesolationPoint', 'OIC', 'CoastalHighway', 'Ravine', 'BleakInlet']
        }
    if len(regions) > 20:
        bases, colours = process_input(fname, style_file=style_file)
        for sr in super_regions:
            these_bases = bases_of_region(bases, super_regions[sr])
            draw_bases(these_bases, colours,
                       base_x=3000, base_y=1200,
                       width=5000, height=3000,
                       output= region_folder + f'ZR-{sr}.svg', output_png=False, print_output=to_print, print_warnings=False)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        print('Drawing', fname)
        if fname.endswith('.json'):
            draw_bases_regionally_and_together(fname)
        else:
            print('To run: python3 TLDBaseViz.py mybases.json')
    else:
        doctest.testmod()
        print('To run: python3 TLDBaseViz.py mybases.json')
        print('Optional parameters to add after the input json filename:')
        print('\t-v \t\t verbose mode')
        print('\t-s {filename} \t use alternate style file')