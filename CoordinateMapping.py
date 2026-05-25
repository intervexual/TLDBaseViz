import doctest

from orca import acss

from TLDBaseViz import *


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
    (1900.0, 2000.0)
    >>> #these_bases['CampOffice'].region_coords # [1100, 1000] before rotation
    [800.0, 1100.0]
    >>> #these_bases['TrappersHomestead'].region_coords  # [100, 1500] before rotation
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
                                 unit_size=10, draw_bg=True,
                                 start_x=0, start_y=0):
    """
    Add the bases in these_bases to the Drawing canvas but don't save it yet
    :param d: Drawing object
    :param these_bases: dict of {str: BaseLocation}, where all bases are in a given region
    :param total_x: width of the region
    :param total_y: height of the region
    :param unit_size: used for spacing out text
    :return:
    """
    boxfill = 'none'
    if draw_bg:
        boxfill = 'white'
    d.append(draw.Rectangle(start_x, start_y, total_x, total_y,
                            fill=boxfill, stroke='#' + 'c'*6, stroke_width=unit_size/2))
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
        coords[region] = Region(region, regions[region]['short'],
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
    >>> region_size_from_coords(bases_of_region(bases, 'HushedRiverValley'))
    (1700, 1750, 300, -50)
    >>> region_size_from_coords(bases_of_region(bases, 'MountainTown'))
    (1800, 2350, 500, -200)
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



#################################

def region_matching(regions):
    for r in regions:
        #print(r, regions[r]['connections'])
        pass

def further_offset_region_coords(these_bases, x_offset, y_offset):
    for b in these_bases:
        bob = these_bases[b]
        if bob.region in regions:
            bob.region_coords[0] += x_offset
            bob.region_coords[1] += y_offset

def get_transitions_for_regions(first_region, second_region, regions):
    """
    Get automatic transition POI name
    :param first_region: str name of region
    :param second_region: str name of region
    :return: two strs of the corresponding matches
    >>> b, e, regions = parse_input('mybases.json')
    >>> get_transitions_for_regions('AshCanyon', 'TimberwolfMountain', regions)
    ('Transition(AC-TWM)', 'Transition(TWM-AC)')
    >>> get_transitions_for_regions('KeepersPass', 'Blackrock', regions)
    ('Transition(KP-BRM)', 'Transition(BRM-KP)')
    """
    ac_short = regions[first_region]['short']
    twm_short = regions[second_region]['short']
    ac_trans = f'Transition({ac_short}-{twm_short})'
    twm_trans = f'Transition({twm_short}-{ac_short})'
    return ac_trans, twm_trans


def line_up_transition_POIs(first_poi, second_poi, ac_bases, twm_bases):
    """

    :param first_poi:
    :param second_poi:
    :param ac_bases:
    :param twm_bases:
    :return:
    """
    ac_x, ac_y = ac_bases[first_poi].region_coords
    twm_x, twm_y = twm_bases[second_poi].region_coords
    rd_x = ac_x - twm_x
    rd_y = ac_y - twm_y
    return rd_x, rd_y


if __name__ == '__main__':
    doctest.testmod()

    dir = 'tests/'
    source_info = 'mybases.json'

    #visit_order = ['AshCanyon', 'TimberwolfMountain', 'PleasantValley', 'KeepersPass', 'Blackrock']
    visit_order = ['ForsakenAirfield', 'TransferPass', 'FarRangeBranchLine',
                   'BrokenRailroad', 'ForlornMuskeg', 'MysteryLake', 'Ravine', "CoastalHighway", "OIC", 'DesolationPoint',
                   'BleakInlet', 'MountainTown', 'HushedRiverValley',
                   'SunderedPass',
                   'ZoneOfContamination',
                   'WindingRiver', 'PleasantValley', 'TimberwolfMountain', 'AshCanyon',
                   'KeepersPass', 'Blackrock']
    #visit_order = [ 'TransferPass', 'FarRangeBranchLine', 'BrokenRailroad', 'ForsakenAirfield', 'SunderedPass', 'ZoneOfContamination']
    special_visit = {'ZoneOfContamination':'TransferPass', 'SunderedPass':'TransferPass',
                     'ForsakenAirfield':'TransferPass',
                     'BleakInlet':'Ravine', 'MountainTown':'ForlornMuskeg',
                     "WindingRiver":"MysteryLake", 'KeepersPass':'PleasantValley'}
    # no direct Transition: DesolationPoint, 'HushedRiverValley', WindingRiver

    """
    PROBLEMS: 
    Blackrock-KP-PV overlaps -- started manual adjustments
    Bleak Inlet does not match up to FM - TODO
    the Far Territory is a mess! -- manual adjustments
    """

    b, e, regions = parse_input(source_info)
    bases, colours = process_input(source_info)
    output = dir + 'combo.svg'

    margin = 50
    unit_size = 10

    # each base object has region_coords
    # 4000, 500 for northlands
    convenience_x = 250
    convenience_y = 3000
    curr_wid = 16000
    curr_hei = 9000
    d = draw.Drawing(curr_wid, curr_hei)
    d.append(draw.Rectangle(0, 0, curr_wid, curr_hei,
                            fill='white'))


    prev_region = ''
    regioned_bases = {} # prev_region: ac_bases
    for i, curr_region in enumerate(visit_order):
        curr_bases = bases_of_region(bases, curr_region)
        add_region_connections(curr_region, regions, bases, curr_bases)

        total_x, total_y, x_offset, y_offset = region_size_from_coords(curr_bases, margin=margin)
        total_x, total_y = calculate_region_coords(curr_bases, regions, curr_region, total_x, total_y, x_offset, y_offset, margin=margin)

        if curr_region in special_visit:
            prev_region = special_visit[curr_region]

        if i == 0:
            further_offset_region_coords(curr_bases, convenience_x, convenience_y)
            rd_x = convenience_x
            rd_y = convenience_y
        else:
            first_poi, second_poi = get_transitions_for_regions(prev_region, curr_region, regions)
            rd_x, rd_y = line_up_transition_POIs(first_poi, second_poi, regioned_bases[prev_region], curr_bases)
            further_offset_region_coords(curr_bases, rd_x, rd_y)

        regioned_bases[curr_region] = curr_bases
        draw_just_region_from_coords(d, curr_bases, total_x, total_y,
                                     unit_size, draw_bg=False,
                                     start_x=rd_x, start_y=rd_y)
        prev_region = curr_region

    d.save_svg(output)