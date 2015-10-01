# MilanCallDensity
Call density in Milan  | Animated Choropleth Map

The **MilanCallDensity** repository contains python code to create an animated choropleth map given the call density data of a day and a grid map over Milan area.

The data and the grid shape file come from the [Telecom Italia Big Data Challenge] (www.telecomitalia.com/bigdatachallenge). 

### Files: ###

* **CallDensityMap.py** : This file contains the code to generate the animated choropleth map. It uses the grid shapefile given in the [Telecom Italia Big Data Challenge] (www.telecomitalia.com/bigdatachallenge). 
Every 15 minutes interval it calculates the call density of each square given by *number of calls / area of the square*. The colour of the square varies according to the value of the density on a scale of Blues.
The colour is assigned according to the bin the density value falls into.
The bins have been created using a technique called [Jenks optimization method] (https://www.wikiwand.com/en/Jenks_natural_breaks_optimization).
It finally creates and save a GIF image **DayCallDensity.GIF**.

* **DayCallDensity.GIF** : This is the result produced by the **CallDensityMap.py**.

* **Transformation/WarmUp.py** : python code to play with shapefiles and analyse the content of the Milan grid shapefile.

* **Transformation/Transformation.py** : set of functions to tranform a grid shapefile from a *UTM32* projection to *WGS84* projection.

* **Transformation/Transformation_test.py** : python code to call the *Transformation* function and reproject a shapefile from a *UTM32* projection to *WGS84* projection.

In order to use this code you need access to the to the [Telecom Italia Big Data Challenge] (www.telecomitalia.com/bigdatachallenge) data.

*NB: The code uses Python 2.7*

