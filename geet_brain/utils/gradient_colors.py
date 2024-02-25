from PIL import Image
import colorsys
from io import BytesIO
import requests


def colorize(thumbnail_path):
    response = requests.get(thumbnail_path)
    thumbnail = Image.open(BytesIO(response.content))

    avg_color = thumbnail.getpixel((1, 45))

    return get_color_shades(avg_color)


def get_color_shades(col):
    contrast = subtractuple((255, 255, 255), hextorgb(scale_lightness(col, "999999")))

    return ("#" + scale_lightness(col, "ababab"),)


def scale_lightness(rgb, grayscale):
    print(rgb)
    h, s, v_desired = colorsys.rgb_to_hsv(*hextorgb(grayscale))
    h_desired, s_desired, v = colorsys.rgb_to_hsv(*rgb)

    return rgbtohex(colorsys.hsv_to_rgb(h_desired, s_desired, v_desired))


def subtractuple(t1, t2):
    return tuple(map(lambda i, j: i - j, t1, t2))


def hextorgb(s):
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def rgbtohex(t):
    return "%02x%02x%02x" % tuple([int(x) for x in t])
