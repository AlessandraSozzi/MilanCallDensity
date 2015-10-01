import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon
from pysal.esda.mapclassify import Natural_Breaks as nb
from descartes import PolygonPatch
import fiona
from itertools import chain

import datetime
from datetime import timedelta

# Convenience functions for working with colour ramps and bars
def colorbar_index(ncolors, cmap, labels=None, **kwargs):
    """
    This is a convenience function to stop you making off-by-one errors
    Takes a standard colour ramp, and discretizes it,
    then draws a colour bar with correctly aligned labels
    
    """
    cmap = cmap_discretize(cmap, ncolors)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors + 0.5)
    colorbar = plt.colorbar(mappable, **kwargs)
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(range(ncolors))
    if labels:
        colorbar.set_ticklabels(labels)
    return colorbar

def cmap_discretize(cmap, N):
    """
    Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.

    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap = djet)

    """
    if type(cmap) == str:
        cmap = get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0., 0., 0., 0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N + 1)
    cdict = {}
    for ki, key in enumerate(('red', 'green', 'blue')):
        cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki]) for i in xrange(N + 1)]
    return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d" % N, cdict, 1024)


filename = '2015-04-17' # Friday 17th April 2015
col_names = ['time', 'square_id', 'callsOut', 'country_code', 'duration']

        
df = pd.read_csv(filename, sep = '\t', names = col_names,
                            usecols = ['time', 'square_id', 'callsOut'],
                            dtype = {'time': long, 'square_id': str, 'callsOut': float})


# Group by cell ID and sum number of calls
# Calls are distinguished between call made from an Italian number or from other 
# country phone numeber (based on the country code)
# For the pourpose of the GIF creation are calls are summed together with no distinction
groupedCalls = df.groupby(['time', 'square_id'], as_index = False).sum()


# Read the shapefile and extract map boundaries
shp = fiona.open('Milano/Milano.shp')
bds = shp.bounds 
shp.close()

extra = 0.02
ll = (bds[0], bds[1])
ur = (bds[2], bds[3])
coords = list(chain(ll, ur))
w, h = coords[2] - coords[0], coords[3] - coords[1] 

# Create a Basemap instance, which we can use to plot the maps on
m = Basemap(
    projection = 'tmerc',
    lon_0 = 9.,
    lat_0 = 45.,
    ellps = 'WGS84',
    llcrnrlon = coords[0] - extra * w,
    llcrnrlat = coords[1] - extra + 0.01 * h,
    urcrnrlon = coords[2] + extra * w,
    urcrnrlat = coords[3] + extra + 0.01 * h,
    lat_ts = 0,
    resolution = 'i',
    suppress_ticks = True) # suppress automatic drawing of axis ticks and labels in map projection coordinates
    
m.readshapefile(
    'Milano/Milano',
    'Milano',
    color = 'none',
    zorder = 2);
    

# Set up a map dataframe
df_map = pd.DataFrame({
    'poly': [Polygon(xy) for xy in m.Milano],
    'square_id': [square['ID'] for square in m.Milano_info]})
df_map['area_m'] = df_map['poly'].map(lambda x: x.area)
df_map['area_km'] = df_map['area_m'] / 1000000

calls = pd.merge(groupedCalls, df_map, how = 'left', on = 'square_id', sort = False)
calls['density_km'] = calls['callsOut'] / calls['area_km']
calls.replace(to_replace={'density_km': {0: np.nan}}, inplace=True)


# Calculate Jenks natural breaks for density
# Classification scheme for choropleth mapping
cuts = 5
breaks = nb(
    calls[calls['density_km'].notnull()].density_km.values,
    initial = 300, # number of initial solutions to generate
    k = cuts) # number of classes required
# The notnull method lets match indices when joining
jb = pd.DataFrame({'jenks_bins': breaks.yb}, index = calls[calls['density_km'].notnull()].index)
calls = calls.join(jb)

binlevels = range(cuts) + [-1] # Possible levels of the bins


# Create a sensible label for classes
# Show density/square km, as well as the number of squares in the class
jenks_labels = ["<= %0.1f/km$^2$" % (b) for b in breaks.bins]
jenks_labels.insert(0, 'No calls made')

# Sorted list of the 15 min time intervals
times = sorted(list(set(calls['time']))) # 96 time intervals (15 x 4 x 24)


# Each 15 min update the color assigned to the square_id
def update_values(t, calls, df_map):
    subset = calls[calls['time'] == t][['square_id', 'density_km', 'jenks_bins']]
    df_map = pd.merge(df_map, subset, how = 'left', on = 'square_id', sort = False)
    df_map.jenks_bins.fillna(-1, inplace=True)
    return df_map['jenks_bins']

# Create 15 min interval image
fmt = '%d-%m-%Y at %H:%M'
for t in times:
    # Updates the jenks_bin values for the square at time t
    # eg t = 1429221600
    df_map['jenks_bins'] = update_values(t, calls, df_map)
    


    plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111, axisbg= 'w', frame_on = False)

    # Use a blue colour ramp
    cmap = plt.get_cmap('Blues')

    # Draw squares with grey outlines
    df_map['patches'] = df_map['poly'].map(lambda x: PolygonPatch(x, ec = '#555555', lw = .2, alpha = 1., zorder = 4))
    pc = PatchCollection(df_map['patches'], match_original = True)

    # Impose colour map onto the patch collection
    norm = Normalize()
    pc.set_facecolor(cmap(norm(np.append(df_map['jenks_bins'].values, binlevels))))
    ax.add_collection(pc)

    # Add a colour bar
    cb = colorbar_index(ncolors = len(jenks_labels), cmap = cmap, shrink = 0.5, labels = jenks_labels)
    cb.ax.tick_params(labelsize = 9)

    
    # Source data info
    smallprint = ax.text(
        0.02, - 0.06, # right from left, down from bottom
        'Source of the Dataset: TIM Big Data Challenge 2015, www.telecomitalia.com/bigdatachallenge',
        ha ='left', va ='bottom',
        size = 8,
        color = '#555555',
        transform = ax.transAxes)
    
    # Draw a map scale
    m.drawmapscale(
        coords[0] + 0.08, coords[1] + 0.015,
        coords[0], coords[1],
        10.,
        barstyle = 'fancy', labelstyle = 'simple',
        fillcolor1 = 'w', fillcolor2 = '#555555',
        fontcolor = '#555555',
        zorder = 5)

    # Set the image width to 820px at 100dpi
    localtimezone = datetime.datetime.fromtimestamp(t) + timedelta(hours = 1)
    title = 'Call density on ' + localtimezone.strftime(fmt) + ', Milano'
    plt.title(title)
    plt.tight_layout()
    fig.set_size_inches(8.2, 5.25)
    img_name = 'imagesDay/' + str(t) + '.png'
    plt.savefig(img_name, dpi = 100, alpha = True)
    plt.show()

    df_map.drop(['jenks_bins'], axis = 1, inplace = True)


# Create gif 
from images2gif import writeGif
from PIL import Image

 
file_names = ['imagesDay/'+ str(fn) +'.png'  for fn in times]

images = [Image.open(fn) for fn in file_names]

size = (820, 525)
for img in images:
    img.thumbnail(size, Image.ANTIALIAS)

filename = "DayCallDensity.GIF"
writeGif(filename, images, duration = 0.2)