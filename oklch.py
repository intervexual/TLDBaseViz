from numbers import Number
import doctest
import numpy as np

# colorm lib:
LMS2LRGB = np.array(
    [
        [4.0767416621, -3.3077115913, 0.2309699292],
        [-1.2684380046, 2.6097574011, -0.3413193965],
        [-0.0041960863, -0.7034186147, 1.707614701],
    ]
).T
# culori lib:
# LMS2LRGB = np.array(
#     [
#         [4.076741661347994, -3.307711590408193, 0.230969928729428],
#         [-1.2684380040921763, 2.6097574006633715, -0.3413193963102197],
#         [-0.004196086541837188, -0.7034186144594493, 1.7076147009309444],
#     ]
# ).T

# # LRGB2LMS = np.linalg.inv(LMS2LRGB)
# colorm lib:
LRGB2LMS = np.array(
    [
        [0.4122214708018041, 0.53633253634543, 0.05144599285276585],
        [0.2119034982505858, 0.6806995451361225, 0.1073969566132915],
        [0.08830246188874209, 0.2817188376235317, 0.6299787004877261],
    ]
).T
# culori lib:
# LRGB2LMS = np.array(
#     [
#         [0.41222147079999993, 0.5363325363, 0.0514459929],
#         [0.2119034981999999, 0.6806995450999999, 0.1073969566],
#         [0.08830246189999998, 0.2817188376, 0.6299787005000002],
#     ]
# ).T

# colorm lib:
OKLAB2CLMS = np.array(
    [
        [1.0, 0.3963377774, 0.2158037573],
        [1.0, -0.1055613458, -0.0638541728],
        [1.0, -0.0894841775, -1.291485548],
    ]
).T
# culori lib:
# OKLAB2CLMS = np.array(
#     [
#         [0.99999999845051981432, 0.39633779217376785678, 0.21580375806075880339],
#         [1.0000000088817607767, -0.1055613423236563494, -0.063854174771705903402],
#         [1.0000000546724109177, -0.089484182094965759684, -1.2914855378640917399],
#     ]
# ).T

# # CLMS2OKLAB = np.linalg.inv(OKLAB2CLMS)
# colorm lib:
CLMS2OKLAB = np.array(
    [
        [0.2104542682745812, 0.7936177747300267, -0.004072043004608028],
        [1.977998532388508, -2.428592241936286, 0.4505937095477779],
        [0.02590404248765818, 0.7827717124269177, -0.8086757549145759],
    ]
).T
# culori lib:
# CLMS2OKLAB = np.array(
#     [
#         [0.2104542553, 0.793617785, -0.0040720468],
#         [1.9779984951, -2.428592205, 0.4505937099],
#         [0.0259040371, 0.7827717662, -0.808675766],
#     ]
# ).T


def args2array(*args):
    if len(args) == 1:
        # convert to array/make sure we're using a copy
        arr = np.array(args[0])
    else:
        arr = np.array(args)
    assert arr.shape[-1] == 3
    return arr


def rgb2oklch(rgb, *args):
    """

    :param rgb:
    :param args:
    :return: array of luminence(0-1), chroma(0-1?),
    >>> rgb2oklch([58, 137, 250])
    array([6.40039378e-01, 1.85514579e-01, 2.57982629e+02])
    >>> rgb2oklch([177, 115, 173])
    array([6.40267829e-01, 1.10091077e-01, 3.29030484e+02])
    >>> rgb2oklch([168, 117, 169])
    array([6.32121090e-01, 9.58832133e-02, 3.25993926e+02])
    >>> rgb2oklch([230, 230, 230]) # hue can be anything because it's grey
    array([0.92493954, 0.        , 0.        ])
    """
    rgb = args2array(rgb, *args)
    if np.issubdtype(rgb.dtype, np.integer):
        # normalize (sometimes called srgb)
        rgb = rgb / 255.0

    # to linear RGB
    sign = np.sign(rgb)
    rgb = np.fabs(rgb)
    lrgb = ((rgb + 0.055) / 1.055) ** 2.4
    lrgb[smol] = rgb[smol := rgb <= 0.04045] / 12.92
    lrgb *= sign

    # to lms
    lms = lrgb @ LRGB2LMS

    # to oklab
    oklab = np.cbrt(lms) @ CLMS2OKLAB

    # to oklch
    oklch = np.zeros_like(oklab)
    oklch[..., 0] = oklab[..., 0]
    okab = oklab[..., 1:]
    chroma = np.linalg.norm(okab, axis=-1)
    # colorm uses this:
    has_chroma = chroma >= 1e-13
    # but if using culori's weights, this is insufficient for some inputs, e.g.,
    # #EBEBEB
    # since we're coming from a discretized space, the following should be
    # acceptable, which works with culori's weights:
    # alternative since we're coming from RGB (and not arbitrary LRGB):
    # has_chroma = (rgb[..., 0] != rgb[..., 1]) | (rgb[..., 1] != rgb[..., 2])
    okab = okab[has_chroma]
    oklch[has_chroma, 1] = chroma[has_chroma]
    oklch[has_chroma, 2] = np.rad2deg(np.arctan2(okab[..., 1], okab[..., 0])) % 360
    return oklch


def _oklch2rgb(oklch, *args):
    """

    :param oklch:
    :param args:
    :return:
    >>> oklch2rgb([0.63212109, 0.0958, 325.99])
    array([168, 117, 169], dtype=uint8)
    >>> oklch2rgb([0.63, 0.09, 326])
    array([166, 118, 166], dtype=uint8)
    >>> oklch2rgb([6.32121090e-01, 9.58832133e-02, 3.25993926e+02])
    array([168, 117, 169], dtype=uint8)
    >>> oklch2rgb([90.0, 0, 0.0])
    Traceback (most recent call last):
    ...
    ValueError: Luminance values must be in [0, 1]
    """
    oklch = args2array(oklch, *args)
    luminance = oklch[..., 0]
    chroma = oklch[..., 1]
    if np.any(luminance < 0) or np.any(luminance > 1):
        raise ValueError("Luminance values must be in [0, 1]")
    if np.any(chroma < 0):
        raise ValueError("Chroma values must be nonnegative")

    # to oklab
    oklab = np.zeros_like(oklch)
    huerad = np.deg2rad(oklch[..., 2])
    oklab[..., 0] = luminance
    oklab[..., 1] = chroma * np.cos(huerad)
    oklab[..., 2] = chroma * np.sin(huerad)

    # to cubic-root lms
    clms = oklab @ OKLAB2CLMS

    # to lrgb
    lrgb = (clms * clms * clms) @ LMS2LRGB

    # to normalized rgb (sometimes called srgb)
    sign = np.sign(lrgb)
    lrgb = np.fabs(lrgb)
    rgb = lrgb ** (1 / 2.4) * 1.055 - 0.055
    rgb[smol] = lrgb[smol := lrgb <= 0.0031308] * 12.92
    rgb *= sign

    return rgb

def _rgb_8bit(rgb):
    # scale and round values
    return np.round(rgb * 255).astype(np.uint8)


def _oog_srgb(rgb):
    return np.any((rgb > 1) | (rgb < 0), axis=-1)


def oklch2rgb(oklch, *args):
    """
    Convert from oklch to sRGB
    :param oklch:
    :param args:
    :return:
    >>> oklch2rgb([0.63212109, 0.0958, 325.99])
    array([168, 117, 169], dtype=uint8)
    >>> oklch2rgb([0.63, 0.09, 326])
    array([166, 118, 166], dtype=uint8)
    >>> oklch2rgb([6.32121090e-01, 9.58832133e-02, 3.25993926e+02])
    array([168, 117, 169], dtype=uint8)
    """
    # adapted from culori library

    oklch = args2array(oklch, *args)
    rgb = _oklch2rgb(oklch)

    # anything that's still OOG when chroma is set to zero should be clipped
    oog = _oog_srgb(rgb)
    if not np.any(oog):
        return _rgb_8bit(rgb)
    oog_srgb = rgb[oog]
    oog_oklch = np.copy(oklch[oog])
    oog_oklch[..., 1] = 0
    oog_zeroed = _oog_srgb(_oklch2rgb(oog_oklch))
    oog_srgb[oog_zeroed] = oog_srgb[oog_zeroed].clip(0, 1)
    rgb[oog] = oog_srgb

    oog = _oog_srgb(rgb)
    if not np.any(oog):
        return _rgb_8bit(rgb)
    oog_oklch = oklch[oog]
    end = oog_oklch[..., 1]
    clamped = np.copy(oog_oklch)
    clamped[..., 1] = 0
    start = np.zeros_like(end)
    last_good = np.zeros_like(end)
    # max SRGB chroma value is ~0.3224; round it up to 0.5 and use
    # resolution = chroma_range / (2 ** 13) = 0.5 / (2 ** 13) = 1 / (2 ** 14)
    resolution = 1 / (1 << 14)
    while np.any(end - start > resolution):
        # a bit inefficient since we don't remove the ones that have met the
        # terminating condition
        clamped[..., 1] = start + (end - start) / 2
        oog_clamped = _oog_srgb(_oklch2rgb(clamped))
        end[oog_clamped] = clamped[oog_clamped, 1]
        start[nogg] = clamped[nogg := ~oog_clamped, 1]
        last_good[nogg] = start[nogg]
    clamped[oog_clamped, 1] = last_good[oog_clamped]
    rgb[oog] = _oklch2rgb(clamped)
    return _rgb_8bit(rgb)


if __name__ == '__main__':
    print(rgb2oklch(58, 137, 250))
    print('res', rgb2oklch([58, 137, 250]))
    print(rgb2oklch([58, 137, 250], [127, 120, 127], [255, 255, 255]))
    print(rgb2oklch([[58, 137, 250], [127, 120, 127], [255, 255, 255]]))
    print(
        rgb2oklch(
            [
                [[58, 137, 250], [127, 120, 127], [255, 255, 255]],
                [[127, 127, 127], [255, 255, 255], [58, 137, 250]],
            ]
        )
    )
    print(
        oklch2rgb(
            [0.640039378, 0.185514579, 257.982629],
            [0.581188542, 0.0134589753, 325.748771],
            [1, 0, 0],
            [0.596489461, 0, 0],
        )
    )


    doctest.testmod()