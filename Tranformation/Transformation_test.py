from Transformation import transform
import os

"""
The function tranform take one argument: the path where the shape file to
transform is located. The function open the shapefile, creates a new one
reprojecting the data with a lat/long projection and save the files in a new
folder in the current directory.
The function return 0 if the transformation succeded

"""
path = os.getcwd()
transform(path)