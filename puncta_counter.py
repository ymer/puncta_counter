from __future__ import division
from itertools import product
import math
import png
from operator import attrgetter
from numpy import average, zeros
from collections import namedtuple
import puncta_counter
import pandas as pd
from glob import glob
import os
import argparse
import sys

Point = namedtuple('Point', 'row col intensity')


def draw_pixels(path, pixels):
    with open(path, 'wb') as f:
        w = png.Writer(len(pixels[0]) // 3, len(pixels))
        w.write(f, pixels)


def add_pixels(points, color, pixels, max_intensity):
    colors = {'red': [1, 0, 0], 'white': [1, 1, 1], 'blue': [0, 0, 1]}
    for point in points:
        if color == 'red':
            for i in range(3):
                pixels[point.row][point.col * 3 + i] = int(colors[color][i] * point.intensity * 255 / max_intensity)
        else:
            for i in range(3):
                pixels[point.row][point.col * 3 + i] = int(colors[color][i] * max_intensity)
    return pixels


def block_direction(centerpoint, image, step, point_cutoff, puncta_high, puncta_low):
    steplength = 1
    p = centerpoint
    blockpoints = [p]
    lowest_intensity = centerpoint.intensity
    while 1:
        row = p.row + step[0] * steplength
        col = p.col + step[1] * steplength
        if not (0 < row < len(image) and 0 < col < len(image[row])):
            break
        intensity = image[row][col]
        if intensity < point_cutoff * 1.1 or intensity > lowest_intensity * puncta_high or intensity < centerpoint.intensity * puncta_low:
            break
        if intensity < lowest_intensity:
            lowest_intensity = intensity
        p = Point(row, col, intensity)
        blockpoints.append(p)
    return blockpoints


def distance_larger_than(p1, p2, dist):
    dim1, dim2 = abs(p1.row - p2.row), abs(p1.col - p2.col)
    return dim1 > dist or dim2 > dist or math.sqrt(dim1**2 + dim2**2) > dist


def read_image(path, color_index=1):
    image = png.Reader(filename=path).read()
    return [row[::color_index] for row in image[2]]


def coords(image):
    for row, col in product(range(len(image)), range(len(image[0]))):
        yield row, col


def get_average_background_intensity(image, bg_image, include_color, background_cutoff):
    return average([image[row][col] for row, col in coords(image) if bg_image[row][col] == include_color and image[row][col] < background_cutoff])


def get_points(image, bg_image, point_cutoff, s):

    points = [Point(row, col, image[row][col]) for row, col in coords(image) if bg_image[row][col] == s.include_color and image[row][col] > point_cutoff and image[row][col] != 255]
    points.sort(key=attrgetter('intensity'), reverse=True)

    centerpoints = []
    blockpoints = []

    for point in points:
        centerpoint = point

        if all(distance_larger_than(centerpoint, blockpoint, s.mindist) for blockpoint in blockpoints):
            centerpoints.append(centerpoint)
            for direction in [prod for prod in product([-1, 0, 1], [-1, 0, 1]) if prod != (0, 0)]:
                blockpoints += block_direction(centerpoint, image, direction, point_cutoff, s.puncta_high, s.puncta_low)

    points = [Point(row, col, image[row][col]) for row in range(len(image)) for col in range(len(image[row])) if bg_image[row][col] == s.include_color]
    return points, centerpoints, blockpoints


def draw(points, centerpoints, blockpoints, dimensions, max_intensity, draw_blocked_points, outpath):

    pixels = zeros((dimensions[0], dimensions[1]*3))
    pixels = add_pixels(points, 'red', pixels, max_intensity)
    if draw_blocked_points:
        pixels = add_pixels(blockpoints, 'blue', pixels, max_intensity)
    pixels = add_pixels(centerpoints, 'white', pixels, max_intensity)
    draw_pixels(outpath, pixels)


def run(imgpath, bg_imgpath, outpath, s):

    bg_image = read_image(bg_imgpath, s.layer_bg)

    image = read_image(imgpath, s.layer_fg)

    if not (len(image) == len(bg_image) and len(image[0]) == len(bg_image[0])):
        raise Exception('Image and background image are not the same dimensions. consider adjusting fg_dim and bg_dim.')

    dimensions = [len(image), len(image[0])]

    average_background_intensity = get_average_background_intensity(image, bg_image, s.include_color, s.background_cutoff)

    point_cutoff = average_background_intensity * s.threshold_multiplier

    points, centerpoints, blockpoints = get_points(image, bg_image, point_cutoff, s)

    draw(points, centerpoints, blockpoints, dimensions, s.max_intensity, s.draw_blocked_points, outpath)

    return len(centerpoints)


def get_area(bg_imgpath, include_color):
    image = read_image(bg_imgpath, 3)
    return len([Point(row, col, image[row][col]) for row, col in coords(image) if image[row][col] != include_color])


def get_settings():
    parser = argparse.ArgumentParser(prefix_chars='--', formatter_class=argparse.RawTextHelpFormatter, add_help=False)
    parser.add_argument('--infolder', default='input', help='\nThe input folder\n\n')
    parser.add_argument('--outfolder', default='output2', help='\nThe output folder\n\n')
    parser.add_argument('--help', action='help', help='\nShow this help message and exit\n\n')
    parser.add_argument('--mindist', default=20, help='\nThe minimum distance between two separate signals\n\n')
    parser.add_argument('--background_cutoff', default=20, help='\nThe intensity below which pixels are viewed as background noise\n\n')
    parser.add_argument('--no_draw_blocked_points', dest='draw_blocked_points', action='store_false', help='Do not draw illustrations of blocked points\n\n')
    parser.add_argument('--threshold_multiplier', default=4, help='\nThe factor by which the intensity of a pixel should be higher than the average background in order to be called as a signal\n\n')
    parser.add_argument('--include_color', default=255, help='\nThe color that pixels in the area we are interested in have in the background image\n\n')
    parser.add_argument('--max_intensity', default=255, help='\n The highest possible pixel intensity on the scale used\n\n')
    parser.add_argument('--layer_bg', default=1, help='\n Number of layers / color depth of background image\n\n')
    parser.add_argument('--layer_fg', default=1, help='\n Number of layers / color depth of main image\n\n')
    parser.add_argument('--puncta_low', default=0.6, help='\n The lowest the intensity can go compared to the intensity of the center of the puncta\n\n')
    parser.add_argument('--puncta_high', default=1.1, help='\n The highest factor that the intensity in a single puncta can increase.\n\n')

    return parser.parse_args(sys.argv[1:])


def main():
    if not os.path.exists(settings.outfolder):
        os.makedirs(settings.outfolder)

    d = {}
    for bg_image in glob(settings.infolder + '/*_line.png'):
        image_name = os.path.basename(bg_image)[:-9] + '.png'
        image = settings.infolder + '/' + image_name
        outpath = settings.outfolder + '/' + image_name

        points = puncta_counter.run(image, bg_image, outpath, settings)
        area = puncta_counter.get_area(bg_image, settings)

        d[image_name] = {'points': points, 'area': area}

    df = pd.DataFrame(d).transpose()
    df['points_per_area'] = df.points / df.area
    df.to_csv(settings.outfolder + '/results.txt', sep=' ', index_label='file')


if __name__ == "__main__":

    settings = get_settings()
    main()


