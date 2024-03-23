from PIL import Image
from math import sqrt
import numpy as np
import threading
import sys

########## pino 27.02.24 ##########
#
#   the script takes a png file and
#   scales it up to 4k resolution
#   and clears up the colors so
#   artifacts near the edges where
#   colors touch are eliminated
#

#######################################################################################
# rgb2lab and lab2rgb are mostly copied from chatgpt to minimize dependencies

def rgb2lab(img):

    width, height, _ = img.shape

    for w in range(width):
        for h in range(height):

            rgb = img[w, h]

            # Normalize RGB values
            r = rgb[0] / 255.0
            g = rgb[1] / 255.0
            b = rgb[2] / 255.0

            # Convert to the sRGB color space
            if r > 0.04045:
                r = ((r + 0.055) / 1.055) ** 2.4
            else:
                r = r / 12.92

            if g > 0.04045:
                g = ((g + 0.055) / 1.055) ** 2.4
            else:
               g = g / 12.92

            if b > 0.04045:
                b = ((b + 0.055) / 1.055) ** 2.4
            else:
                b = b / 12.92

            # Convert to XYZ color space
            X = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
            Y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
            Z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

            # Normalize XYZ values
            X = X / 0.95047
            Z = Z / 1.08883

            # Convert to LAB color space
            if X > 0.008856:
                X = X ** (1/3)
            else:
                X = (7.787 * X) + (16 / 116)

            if Y > 0.008856:
                Y = Y ** (1/3)
            else:
                Y = (7.787 * Y) + (16 / 116)

            if Z > 0.008856:
                Z = Z ** (1/3)
            else:
                Z = (7.787 * Z) + (16 / 116)

            L = (116 * Y) - 16
            a = 500 * (X - Y)
            b = 200 * (Y - Z)

            img[w, h] = (L, a, b)

    return img

def lab2rgb(img):

    width, height, _ = img.shape

    for w in range(width):
        for h in range(height):

            lab = img[w, h]

            # Convert LAB to XYZ
            Y = (lab[0] + 16) / 116
            X = lab[1] / 500 + Y
            Z = Y - lab[2] / 200

            if Y ** 3 > 0.008856:
                Y = Y ** 3
            else:
                Y = (Y - 16 / 116) / 7.787

            if X ** 3 > 0.008856:
                X = X ** 3
            else:
                X = (X - 16 / 116) / 7.787

            if Z ** 3 > 0.008856:
                Z = Z ** 3
            else:
                Z = (Z - 16 / 116) / 7.787

            X = X * 0.95047
            Y = Y * 1.00000
            Z = Z * 1.08883

            # Convert XYZ to RGB
            r = X *  3.2404542 - Y * 1.5371385 - Z * 0.4985314
            g = -X * 0.9692660 + Y * 1.8760108 + Z * 0.0415560
            b = X * 0.0556434 - Y * 0.2040259 + Z * 1.0572252

            # Apply gamma correction
            if r > 0.0031308:
                r = 1.055 * (r ** (1 / 2.4)) - 0.055
            else:
                r = 12.92 * r

            if g > 0.0031308:
                g = 1.055 * (g ** (1 / 2.4)) - 0.055
            else:
                g = 12.92 * g

            if b > 0.0031308:
                b = 1.055 * (b ** (1 / 2.4)) - 0.055
            else:
                b = 12.92 * b

            # Clip the values to the range [0, 1]
            r = max(0, min(1, r))
            g = max(0, min(1, g))
            b = max(0, min(1, b))

            # Scale to the range [0, 255] and round to integers
            r = round(r * 255)
            g = round(g * 255)
            b = round(b * 255)

            img[w, h] = (r, g, b)

    return img

#######################################################################################

def upscale(img):

    height, width, _ = img.shape
    scale_factor = max(3840 / height, 2160 / width)
    new_height = int(height * scale_factor)
    new_width = int(width * scale_factor)

    return img.resize((new_height, new_width), Image.LANCZOS)

# takes an image in lab format and clears up artifacts # TODO: doesnt work as i thought it would
def clear_up(img, delta):

    width, height, _ = img.shape

    colors = []
    color_distribution = np.zeros((width, height), dtype=int)
    img_clear = np.zeros((width, height, 3), dtype=np.uint8)

    colors.append(img_rgb[0,0])

    # iterate image to collect colors
    for w in range(width):
        print("progress: "+str(w)+"/"+str(width)+" lines")
        for h in range(height):

            l1, a1, b1 = img[w, h]

            for i, color in enumerate(colors):

                l2, a2, b2 = color
                deltaE = sqrt((l2 - l1) ** 2 + (a2 - a1) ** 2 + (b2 - b1) ** 2)

                # if colors are similar, remember in color_distribution
                if deltaE <= delta:
                    color_distribution[w, h] = i
                    break

            # if colors are not similar enough, add it as new color
            if deltaE > delta:
                colors.append(img_rgb[w, h])
                color_distribution[w, h] = len(colors)-1

    print("simplified to "+str(len(colors))+" colors")

    # generate output
    for w in range(width):
        for h in range(height):

            img_clear[w, h] = colors[color_distribution[w, h]]

    return img_clear

if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("error: wrong number of arguments!")
        print("usage: pxlart-upscaler.py <delta> <input>.png <output>.png")
        sys.exit(1)

    input = Image.open(sys.argv[2])
    img_upscaled = upscale(input)

    img_rgb = np.array(img_upscaled)
    img_lab = rgb2lab(img_rgb)
    delta = float(sys.argv[1])
    img_clear = clear_up(img_lab, delta)
    result = lab2rgb(img_clear)

    image = Image.fromarray(result)
    image.save(sys.argv[3])