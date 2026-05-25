"""
Visualize the different times of day in The Long Dark
"""
from keysAndDefs import *


moon_fname = 'assets/moon.svg'
sun_fname = 'assets/sun.svg'
icon_size = 100



def get_triangle_coords(rad, arc_width, i, x_mid, y_mid, offset=-90, x_skew=1.0, y_skew=1.0):
    """
    Helper function for drawing segmented rings, Seychelles flags, and other polar math
    :param rad: radius
    :param arc_width: the arc width of a segment
    :param i: which segment we're on
    :param x_mid: the coordinate of the centre (x)
    :param y_mid: the coordinate of the centre (y)
    :param offset: angle in degrees of offset from where we start the segmentation
    :return: coordinates
    >>> get_triangle_coords(10, 45, 1, 0, -45)
    (7.0710678118654755, -52.071067811865476)
    """
    x = (rad*x_skew) * math.cos(math.radians(offset + arc_width * i)) + x_mid
    y = (rad*y_skew) * math.sin(math.radians(offset + arc_width * i)) + y_mid
    return x, y



def draw_hud_time(angle, outfile='test.svg', label='', fill='white'):
    """
    Draw a diagram of the time of day in the style of the HUD in The Long Dark
    :param angle: angle of rotation (0 degrees is 18h, each hour is 15 degrees of rotation)
    :param outfile: output file name
    :param label: text label (e.g. '18:00')
    :param fill: colour used for sun, moon, text
    :return: nothing
    """
    sky_height = icon_size*2.5
    horizon_height = icon_size*1.5
    horizon_y = sky_height

    canhei = horizon_height + sky_height
    canwid = icon_size*5

    d = draw.Drawing(canwid, canhei)

    sky = draw.Rectangle(0, 0, canwid, sky_height, fill='grey')
    horizon = draw.Rectangle(0, horizon_y, canwid, horizon_height, fill='black')

    # centre of rotation
    cor_x = canwid/2
    cor_y = horizon_y

    # TODO ensure this distance is correct!
    # https://thelongdark.fandom.com/wiki/Survival_Overlay
    # says that 20:30 is when daytime ends & nighttime begins
    # at .92, the moon is not high enough at 20:30
    dist_between_sun_and_moon = icon_size*.95
    angle_dist_between_sun_and_moon = 180

    sun_mid_x, sun_mid_y = get_triangle_coords(dist_between_sun_and_moon, angle_dist_between_sun_and_moon, 0, x_mid=cor_x, y_mid=cor_y, offset=angle)
    moon_mid_x, moon_mid_y = get_triangle_coords(dist_between_sun_and_moon, angle_dist_between_sun_and_moon, 1, x_mid=cor_x, y_mid=cor_y, offset=angle)

    # add to canvas in order: sky, sun & moon, horizon
    d.append(sky)

    sun_x = sun_mid_x - icon_size/2
    sun_y = sun_mid_y - icon_size/2
    sun = import_svg(d, sun_fname, sun_x, sun_y, icon_size, icon_size, fill=fill)

    moon_x = moon_mid_x - icon_size/2
    moon_y = moon_mid_y - icon_size/2
    moon = import_svg(d, moon_fname, moon_x, moon_y, icon_size, icon_size, fill=fill)
    d.append(horizon)

    text_x = cor_x + icon_size*.4
    text_y = horizon_y +  icon_size*.6
    text_size = 40
    d.append(draw.Text(label, text_size, text_x, text_y,
                       text_anchor='end',
                       fill=fill))
    if outfile.endswith('.svg'):
        d.save_svg(outfile)
    else:
        d.save_png(outfile)


def ang_to_time(ang):
    """
    Convert angle of rotation to time as string
    :param ang: angle in degrees
    :return: string in 24h time format
    >>> ang_to_time(0)
    '18:00'
    >>> ang_to_time(15)
    '19:00'
    >>> ang_to_time(-15)
    '17:00'
    >>> ang_to_time(15/2)
    '18:30'
    >>> ang_to_time(15/4)
    '18:15'
    >>> ang_to_time(90)
    '0:00'
    """
    h = ang // 15
    hour = int( (h + 18) % 24 )
    diff = ang - h*15
    min = int(diff/.25)
    return f'{hour}:{min:02}'



ang_inc = 15/2
ang = 0
while ang < 360:
    hour = ang_to_time(ang)
    print(hour, ang)
    draw_hud_time(ang, outfile=f'time/{hour}.svg', label=hour)
    ang += ang_inc


reps = 2
ang_inc = 15/2
ang = 0
iter = 0

iter_start = 5
while iter < iter_start:
    draw_hud_time(ang, outfile=f'time/anim/img_{iter:03d}.png', label=hour)
    iter += 1

while ang < 360*2:
    hour = ang_to_time(ang)
    #print(hour, ang)
    draw_hud_time(ang, outfile=f'time/anim/img_{iter:03d}.png', label=hour)
    ang += ang_inc
    iter += 1

iter_end = iter + iter_start*2
while iter < iter_end:
    draw_hud_time(ang, outfile=f'time/anim/img_{iter:03d}.png', label=hour)
    iter += 1

# ffmpeg -framerate 5 -i img_%03d.png output5.mp4

doctest.testmod()