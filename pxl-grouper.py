import sys
import numpy as np
from PIL import Image

########## pino 23.03.24 ##########
#
#   the script takes a png file and
#   scales it up to 4k resolution
#   and makes blocks of variable
#   size of one color
#


# iterates over the image and groups multiple pixels to their average color 
def group_pixels(img, block_size):

        height, width, _ = img.shape

        for y in range(0, height-block_size, block_size):
            for x in range(0, width-block_size, block_size):

                r_sum = 0
                g_sum = 0
                b_sum = 0

                for h in range(y, y+block_size):
                    for w in range(x, x+block_size):
                          
                        r_sum = r_sum + img[h, w, 0]
                        g_sum = g_sum + img[h, w, 1]
                        b_sum = b_sum + img[h, w, 2]

                r = r_sum / block_size**2
                g = g_sum / block_size**2
                b = b_sum / block_size**2

                for h in range(y, y+block_size):
                    for w in range(x, x+block_size):
                         
                        img[h, w, 0] = r
                        img[h, w, 1] = g
                        img[h, w, 2] = b

        return img


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("error: wrong number of arguments!")
        print("usage: pxl-grouper.py <block_size> <input>.png <output>.png")
        sys.exit(1)

    block_size = int(sys.argv[1])
    img = Image.open(sys.argv[2])
    arr = np.array(img)
    output_path = sys.argv[3]

    arr = group_pixels(arr, block_size)

    img = Image.fromarray(arr, mode="RGB")
    img.save(output_path)