The software detects and quantifies synaptic puncta from PNG format images obtained from fluorescently stained cell cultures.

Guide:

- Take pictures in 60x magnification. Convert images to greyscale png.

- Install pypng. (https://pypi.python.org/pypi/pypng)

- Mark the synapse in a seperate file. The synapse is colored white, while the non-synapse area is any other color.

- Put all the files in one folder. For each image, the corresponding marking file should be called [image name]_line.png.

- Adjust line 27-28 in run.py to have the correct folder names.

- Run run.py.

- Check the resulting puncta identification in the output folder. Adjust the settings in line 11-24 in run.py, and run again.