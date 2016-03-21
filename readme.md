The software detects and quantifies synaptic puncta from PNG format images obtained from fluorescently stained cell cultures.

Guide:

- Take pictures in 60x magnification. Convert images to greyscale png.

- Install pypng. (https://pypi.python.org/pypi/pypng)

- Mark the synapse in a seperate file. The synapse is colored white, while the non-synapse area is any other color.

- Put all the files in one folder. For each image, the corresponding marking file should be called [image name]_line.png.

- Run the program
 
- Check the resulting puncta identification in the output folder. Adjust the settings, and run again.


Arguments: 

  --infolder INFOLDER   
                        The input folder
                        
  --outfolder OUTFOLDER
                        
                        The output folder
                        
  --help                
                        Show this help message and exit
                        
  --mindist MINDIST     
                        The minimum distance between two separate signals
                        
  --background_cutoff BACKGROUND_CUTOFF
                        
                        The intensity below which pixels are viewed as background noise
                        
  --no_draw_blocked_points
                        Do not draw illustrations of blocked points
                        
  --threshold_multiplier THRESHOLD_MULTIPLIER
                        
                        The factor by which the intensity of a pixel should be higher than the average background in order to be called as a signal
                        
  --include_color INCLUDE_COLOR
                        
                        The color that pixels in the area we are interested in have in the background image
                        
  --max_intensity MAX_INTENSITY
                        
                         The highest possible pixel intensity on the scale used
                        
  --layer_bg LAYER_BG   
                         Number of layers / color depth of background image
                        
  --layer_fg LAYER_FG   
                         Number of layers / color depth of main image
                        
  --puncta_low PUNCTA_LOW
                        
                         The lowest the intensity can go compared to the intensity of the center of the puncta
                        
  --puncta_high PUNCTA_HIGH
                        
                         The highest factor that the intensity in a single puncta can increase.
                        
