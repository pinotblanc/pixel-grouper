import sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def load_image(path):
        
        return np.uint8(plt.imread(path) * 255)

def image2pixels(image):
        
    out = []
    y_max, x_max, _ = image.shape

    for y in range(y_max):
        for x in range(x_max):

            out.append((*image[y][x], x, y))

    return out

def pixels2image(pixels):
     
    y_max = max([pixel[4] for pixel in pixels])
    x_max = max([pixel[3] for pixel in pixels])
    out = np.zeros([y_max+1, x_max+1, 3], dtype=np.uint8)

    for pixel in pixels:

        r, g, b, x, y = pixel
        out[y][x] = np.array([r, g, b], dtype=np.uint8)

    return out

def bounding_box(pixels):
     
    reds = [pixel[0] for pixel in pixels]
    greens = [pixel[1] for pixel in pixels]
    blues = [pixel[2] for pixel in pixels]

    return (min(reds), max(reds)), (min(greens), max(greens)), (min(blues), max(blues))

def color_average(pixels):
     
    reds = [pixel[0] for pixel in pixels]
    greens = [pixel[1] for pixel in pixels]
    blues = [pixel[2] for pixel in pixels]
    length = len(pixels)

    return round(sum(reds) / length), round(sum(greens) / length), round(sum(blues) / length)

def cut_dimension(bbox):

    r = bbox[0][1] - bbox[0][0]
    g = bbox[1][1] - bbox[1][0]
    b = bbox[2][1] - bbox[2][0]
    maximum = max(r, g, b)

    return 0 if maximum == r else 1 if maximum == g else 2


def recursive_median_cut(pixels, N):

    if len(pixels) < 2:
        return pixels
    if N == 0:
        (ravg, gavg, bavg) = color_average(pixels)
        return [(ravg, gavg, bavg, pixel[3], pixel[4]) for pixel in pixels]

    axis = cut_dimension(bounding_box(pixels))

    pixels.sort(key=lambda t: t[axis])

    part1 = pixels[:len(pixels)//2]
    part2 = pixels[len(pixels)//2:]

    return recursive_median_cut(part1, N-1) + recursive_median_cut(part2, N-1)


def median_cut(image, ncuts=8):

    pixels = image2pixels(image)
    pixels = recursive_median_cut(pixels, ncuts)
    return pixels2image(pixels)


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("error: wrong number of arguments!")
        print("usage: mediancut.py <iterations> <input>.png <output>.png")
        sys.exit(1)

    # init
    n = int(sys.argv[1])
    img = load_image(sys.argv[2])

    img = median_cut(img, n)

    img = Image.fromarray(img, mode="RGB")
    img.save(sys.argv[3])