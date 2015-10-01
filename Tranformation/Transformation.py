import os, os.path, shutil
from osgeo import ogr
from osgeo import osr
import glob
import re

    
def open_shp(path):
    filename = glob.glob(str(path) + "/*.shp")[0]
    shp_file = ogr.Open(filename)
    if shp_file is None:
        print 'Could not open shape file in directory %s' % (path)
        return (None, None)
    
    # The original filenames are in the form of intersection_City_W_GRIDIT_NEW.shp
    # Extract the city name
    if '_' in filename:
        city = re.split('_', filename)[1]
        return (shp_file, city)
    
    return shp_file

def create_dir(city):
    if os.path.exists(city):
        shutil.rmtree(city)
    os.mkdir(city)
    return city

    
def reproject(srcFile, dstFile) :
    
    srcProjection = osr.SpatialReference()
    srcProjection.SetUTM(32)
    dstProjection = osr.SpatialReference()
    dstProjection.SetWellKnownGeogCS('WGS84') # Lat/long.
    transformation = osr.CoordinateTransformation(srcProjection, dstProjection)
    
    srcLayer = srcFile.GetLayer(0)
    dstLayer = dstFile.CreateLayer("layer", dstProjection)
    
    layer = srcFile.GetLayer(0)
    feature = layer.GetFeature(0)
    attributes = feature.keys()
    for key in attributes:
        fieldDef = ogr.FieldDefn(key, ogr.OFTString)
        fieldDef.SetWidth(50)
        dstLayer.CreateField(fieldDef)
    
    # Reproject each feature in turn
    for i in range(srcLayer.GetFeatureCount()):
        feature = srcLayer.GetFeature(i)
        geometry = feature.GetGeometryRef()
        newGeometry = geometry.Clone()
        newGeometry.Transform(transformation)
        newFeature = ogr.Feature(dstLayer.GetLayerDefn())
        newFeature.SetGeometry(newGeometry)
        attributes = feature.keys()
        for attribute in attributes:
            featureValue = feature.GetField(attribute)
            newFeature.SetField(attribute, featureValue) 
        dstLayer.CreateFeature(newFeature)
        newFeature = None
        feature = None
            
    
def transform(srcPath):
    srcFile, city = open_shp(srcPath)
    
    # Tranform file
    if all([srcFile is not None, city is not None]):
        dstPath = create_dir(city)
        filename = city + ".shp"
        filePath = os.path.join(city, filename)
        
        # Define Driver
        driver = ogr.GetDriverByName("ESRI Shapefile")
    
        dstFile = driver.CreateDataSource(filePath)
        
        reproject(srcFile, dstFile) 
    
    srcFile = None
    dstFile = None
             
    return 0




############### TEST ################

path = os.getcwd()
transform(path)

