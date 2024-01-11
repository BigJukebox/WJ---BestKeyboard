from PIL import Image, ImageFont, ImageDraw
from colour import Color

def interpolate(color, targetcolor, gradient):
    r1, g1, b1 = color
    r2, g2, b2 = targetcolor
    r3 = r2 - r1
    g3 = g2 - g1
    b3 = b2 - b1


    r = (int(r1 + r3*gradient)%256, int(g1 + g3*gradient)%256, int(b1 + b3*gradient)%256)
    return r



heatmappreset = {"red": "yellow-red", "blue": "blue-yellow", 0: "blue-yellow", 1: "yellow-red"}


# ------------Settings----------------

_mark_ = 5
_markcolor_ = (214, 83, 60)

_colormap_ = True
_heatmaptype_ = "blue-yellow"



offset = 20
# ------------------------------------



def generatekeyboard(keyboard, mark = None, markcolor = None, colormap = None, heatmaptype = None):
    #init settings
    if mark is None: mark = _mark_
    if markcolor is None: markcolor = _markcolor_
    if colormap is None: colormap = _colormap_
    if heatmaptype is None: heatmaptype = _heatmaptype_


    if colormap: mark = False

    heatmaptype = heatmaptype.split("-")
    colors = list(Color(heatmaptype[0]).range_to(Color(heatmaptype[1]), 1000))



    keys = keyboard

    ordered = ["e", "n", "i", "s", "r", "a", "t", "d", "h", "u", "l", "c", "g", "m", "o", "b", "w", "f", "k", "z", "p", "v", "ü", "ä", "ö", "ß", "j", "y", "x", "q"]
    marklist = ordered[:mark]

    frequency = {"e": 17.09, "n": 9.61, "i": 7.42, "s": 7.14, "r": 6.87, "a": 6.39, "t": 6.04, "d": 4.99, "h": 4.67, "u": 4.27, "l": 3.38, "c": 3.01, "g": 2.96, "m": 2.48, "o": 2.47, "b": 1.86, "w": 1.86, "f": 1.63, "k": 1.19, "z": 1.11, "p": 0.78, "v": 0.66, "ü": 0.63, "ä": 0.5, "ö": 0.35, "ß": 0.3, "j": 0.27, "y": 0.04, "x": 0.03, "q": 0.02}
    frequencymax = 17.09
    frequencymin = 0.02


    image = Image.open("C:\\Users\\max.stephan\\Desktop\\Projects\\KeyboardRundown\\blankkeyboard2.png").convert("RGB")
    draw = ImageDraw.Draw(image)


    ## generate key positions
    # a = [129, 205, 280]
    # a2 = {129: 129, 205: 141, 280: 174}
    # coords = []
    # for j in a:
    #     for i in range(12):
    #         coords.append((a2[j]+71*i + int(i/3), j))
    # coords.pop(-1)
    # coords.pop(-1)
    # coords.append((103, 280))

    coords = [(129, 129), (200, 129), (271, 129), (343, 129), (414, 129), (485, 129), (557, 129), (628, 129), (699, 129), (771, 129), (842, 129), (913, 129), (141, 205), (212, 205), (283, 205), (355, 205), (426, 205), (497, 205), (569, 205), (640, 205), (711, 205), (783, 205), (854, 205), (925, 205), (174, 280), (245, 280), (316, 280), (388, 280), (459, 280), (530, 280), (602, 280), (673, 280), (744, 280), (816, 280), (103, 280)]






    normalfont = ImageFont.truetype("C:\\Users\\max.stephan\\Desktop\\Projects\\KeyboardRundown\\font\\Tenso-Regular.otf", 29)
    offsetfont= ImageFont.truetype("C:\\Users\\max.stephan\\Desktop\\Projects\\KeyboardRundown\\font\\Tenso-Regular.otf", 22)

    # drawing text size
    for i in range(len(keys)):
        cord = coords[i]

        #change key color
        if mark:
            if keys[i][0].lower() in marklist: ImageDraw.floodfill(image, cord, markcolor, thresh=40)
        if colormap:
            if keys[i][0] in frequency.keys():
                #val = int((math.log(frequency[keys[i][0].lower()])-math.log(frequencymin)+1)/(math.log(frequencymax)-math.log(frequencymin)+1)*1000)
                val = int((frequency[keys[i][0].lower()])/(frequencymax)*1000)
                if val == 0: val = 1
                c = colors[val-1]
                rgb = (int(c.get_red()*255)%256, int(c.get_green()*255)%256, int(c.get_blue()*255)%256)
                rgb = interpolate(rgb, (190, 195, 221), 0.4)
                ImageDraw.floodfill(image, cord, rgb, thresh=40)



        for j in range(len(keys[i])):
            if j == 0:
                draw.text(cord, keys[i][j].upper(), fill="black", font=normalfont, align="middle")
                continue

            if j == 1:
                x, y = cord
                newcord = (x+offset, y-offset+7)
            elif j == 2:
                x, y = cord
                newcord = (x+offset, y+offset)
            draw.text(newcord, keys[i][j].upper(), fill="black", font=offsetfont, align="middle")


    return image


def showkeyboard(keyboard, mark = None, markcolor = None, colormap = None, heatmaptype = None):
    generatekeyboard(keyboard, mark, markcolor, colormap, heatmaptype).show()