from __future__ import division
from itertools import product
import math
import png
from operator import attrgetter
from numpy import average, zeros


class Point:
    def __init__(self, row, col, intensity):
        self.row = row
        self.col = col
        self.intensity = intensity

    def __str__(self):
        return str(self.row) + ", " + str(self.col) + ", " + str(self.intensity)


def draw_pixels(path, pixels):
    with open(path, 'wb') as f:
        w = png.Writer(len(pixels[0]) / 3, len(pixels))
        w.write(f, pixels)


def add_pixels(points, color, pixels, max_intensity):
    colors = {"red": [1, 0, 0], "white": [1, 1, 1], "blue": [0, 0, 1]}
    for point in points:
        if color == "red":
            for i in range(3):
                pixels[point.row][point.col * 3 + i] = colors[color][i] * point.intensity * 255 / max_intensity
        else:
            for i in range(3):
                pixels[point.row][point.col * 3 + i] = colors[color][i] * max_intensity
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
    if dim1 > dist or dim2 > dist:
        return True
    return math.sqrt(dim1**2 + dim2**2) > dist


def read_image(path, color_index=1):
    r = png.Reader(filename=path)
    a = r.read()
    return [row[::color_index] for row in a[2]]


def coords(image):
    for row, col in product(range(len(image)), range(len(image[0]))):
        yield row, col


def get_average_background_intensity(image, bg_image, include_color, background_cutoff):
    return average([image[row][col] for row, col in coords(image) if bg_image[row][col] == include_color and image[row][col] < background_cutoff])


def get_points(image, bg_image, point_cutoff, s):

    points = [Point(row, col, image[row][col]) for row, col in coords(image) if bg_image[row][col] == s.include_color and image[row][col] > point_cutoff and image[row][col] != 255]
    points.sort(key=attrgetter("intensity"), reverse=True)

    centerpoints = []
    blockpoints = []

    index = 0
    while index < len(points):
        centerpoint = points[index]

        if all(distance_larger_than(centerpoint, blockpoint, s.mindist) for blockpoint in blockpoints):
            centerpoints.append(centerpoint)
            for direction in [prod for prod in product([-1, 0, 1], [-1, 0, 1]) if prod != (0, 0)]:
                blockpoints += block_direction(centerpoint, image, direction, point_cutoff, s.puncta_high, s.puncta_low)
        index += 1

    points = [Point(row, col, image[row][col]) for row in range(len(image)) for col in range(len(image[row])) if bg_image[row][col] == s.include_color]
    return points, centerpoints, blockpoints


def draw(points, centerpoints, blockpoints, dimensions, max_intensity, draw_blocked_points, outpath):

    print dimensions
    pixels = zeros((dimensions[0], dimensions[1]*3))
    pixels = add_pixels(points, "red", pixels, max_intensity)
    if draw_blocked_points:
        for point in blockpoints:
            point.intensity = max_intensity
        pixels = add_pixels(blockpoints, "blue", pixels, max_intensity)
    for point in centerpoints:
        point.intensity = max_intensity
    pixels = add_pixels(centerpoints, "white", pixels, max_intensity)
    draw_pixels(outpath, pixels)


def run(imgpath, bg_imgpath, outpath, s):

    bg_image = read_image(bg_imgpath, s.layer_bg)

    image = read_image(imgpath, s.layer_fg)

    if not (len(image) == len(bg_image) and len(image[0]) == len(bg_image[0])):
        print 'image dim', len(image), len(image[0])
        print 'bg image dim', len(bg_image), len(bg_image[0])
        raise Exception('Image and background image are not the same size. consider adjusting fg_dim and bg_dim.')

    dimensions = [len(image), len(image[0])]

    average_background_intensity = get_average_background_intensity(image, bg_image, s.include_color, s.background_cutoff)

    point_cutoff = average_background_intensity * s.threshold_multiplier

    points, centerpoints, blockpoints = get_points(image, bg_image, point_cutoff, s)

    draw(points, centerpoints, blockpoints, dimensions, s.max_intensity, s.draw_blocked_points, outpath)

    return len(centerpoints)


def get_area(bg_imgpath, include_color):
    image = read_image(bg_imgpath, 3)
    return len([Point(row, col, image[row][col]) for row, col in coords(image) if image[row][col] != include_color])
