from __future__ import division
import puncta_counter
import pandas as pd
from glob import glob
import os


class Settings:
    pass

settings = Settings()
settings.mindist = 20  # The minimum distance between two separate signals
settings.background_cutoff = 20  # The intensity below which pixels are viewed as background noise
settings.draw_blocked_points = True
settings.threshold_multiplier = 4  # The factor by which the intensity of a pixel should be higher than the average
                          # background in order to be called as a signal
settings.include_color = 255   # The color that pixels in the area we are interested in have.
settings.max_intensity = 255  # The highest possible pixel intensity on the scale used.

settings.layer_bg = 1  # Number of layers / color depth of background image
settings.layer_fg = 1  # Number of layers / color depth of main image

settings.puncta_low = 0.6  # The lowest the intensity can go compared to the intensity of the center of the puncta.
settings.puncta_high = 1.1  # The highest factor that the intensity in a single puncta can increase


folder = ''
outfolder = ''

d = {}

for bg_image in glob(folder + '*_line.png'):
    image_name = os.path.basename(bg_image)[:-9] + '.png'
    print image_name
    image = folder + image_name
    outpath = outfolder + image_name

    points = puncta_counter.run(image, bg_image, outpath, settings)
    area = puncta_counter.get_area(bg_image, settings)

    d[image_name] = {'points': points, 'area': area}

df = pd.DataFrame(d).transpose()
df['points_per_area'] = df.points / df.area
df.to_csv(outfolder + 'results.txt', sep=' ', index_label='file')
