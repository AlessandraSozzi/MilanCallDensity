import osgeo.ogr

shapefile = osgeo.ogr.Open("intersection_Torino_W_GRIDIT_NEW.shp")
numLayers = shapefile.GetLayerCount()
print "Shapefile contains %d layers" % numLayers
# Shapefile contains 1 layers
print

"""
SPATIAL REF =   specifies the projection and datum used by the layer's data.

PROJECTION =    A projection is a mathematical transformation that "unwraps" 
                the three-dimensional shape of the earth and places it onto a 
                two-dimensional plane.
DATUM =         A datum is a mathematical model of the earth used to describe 
                locations on the earth's surface. A datum consists of a set of 
                reference points, often combined with a model of the shape of 
                the earth. The reference points are used to describe the 
                location of other points on the earth's surface, while the 
                model of the earth's shape is used when projecting the earth's 
                surface onto a two-dimensional plane. 
                eg.'WGS84': The World Geodetic System of 1984.
                
FEATURE =       corresponds to some significant element within the layer, 
                in this case each feature correspond to a square.
                Each feature has a list of attributes and a geometry.
                
ATTRIBUTES =    provide additional meta-information about the feature, eg. the 
                feature's unique ID, which can be used to connect to the other 
                datasets.
                
GEOMETRY =      The geometry describes the physical shape or location of the 
                feature.

"""
for layerNum in range(numLayers):
    layer = shapefile.GetLayer(layerNum)
    spatialRef = layer.GetSpatialRef().ExportToProj4()
    numFeatures = layer.GetFeatureCount()
    print "Layer %d has spatial reference %s" % (layerNum, spatialRef)
    # Layer 0 has spatial reference +proj=utm +zone=32 +datum=WGS84 +units=m +no_defs
    
    
    print "Layer %d has %d features:" % (layerNum, numFeatures)
    # Layer 0 has 1419 features


    print
    
    # Print each feature and corresponding attribute ID (Id of the square)
    for featureNum in range(numFeatures):
        feature = layer.GetFeature(featureNum)
        featureID = feature.GetField("ID")
        print "Feature %d has Id %s" % (featureNum, featureID)
        

# Analysis of feature 0
layer = shapefile.GetLayer(0)
feature = layer.GetFeature(2)
print "Feature 2 has the following attributes:"
print
attributes = feature.items()
for key,value in attributes.items():
    print " %s = %s" % (key, value)
    # Each feature has only one attrinbute (Id of the square)



"""
Geometries are recursive data structures that can themselves contain sub-geometries
A geometry object is a complex structure that holds some geospatial data, 
often using nested geometry objects to reflect the way the geospatial data 
is organized. 

"""

# Analysis of the shapefile geometry
geometry = feature.GetGeometryRef()
geometryName = geometry.GetGeometryName()
print
print "Feature's geometry data consists of a %s" % geometryName

"""
Polygons are commonly used in geospatial data to describe the outline of 
countries, lakes, cities, and so on. A polygon has an exterior ring, defined 
by a closed linestring, and may optionally have one or more interior rings 
within it, each also defined by a closed linestring. The exterior ring 
represents the polygon's outline, while the interior rings (if any) represent 
'holes' within the polygon.

"""

def analyzeGeometry(geometry, indent=0):
    s = []
    s.append(" " * indent)
    s.append(geometry.GetGeometryName())
    if geometry.GetPointCount() > 0:
        s.append(" with %d data points" % geometry.GetPointCount())
    if geometry.GetGeometryCount() > 0:
        s.append(" containing:")
    
    print "".join(s)
    for i in range(geometry.GetGeometryCount()):
        analyzeGeometry(geometry.GetGeometryRef(i), indent+1)


analyzeGeometry(geometry)
