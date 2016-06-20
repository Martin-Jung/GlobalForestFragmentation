# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 15:01:48 2016

@author: martin
"""
import numpy as np
from osgeo import osr
from osgeo import gdal

import os,sys
from os import path
import tarfile
from glob import glob

def show(array):
         import matplotlib.pyplot as plt
         plt.imshow(array,interpolation='nearest')
         plt.axis('on')
         plt.show()


def deleteDir(where):
    """
    Delete first all files and then the dir
    """
    for root, dirs, files in os.walk(where, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(where)

def untar(fname,where):
    """
    Extracts all content from a given tar.gz file
    into a new folder
    """
    if (fname.endswith("tar.gz")):
        tar = tarfile.open(fname)
        # Create folder if not already existing
        if path.exists(where) == False:
            os.mkdir(where)
        tar.extractall(path=where)
        tar.close()

def cellsize(pa):
    """
    Opens a given path and returns the cellsize
    from a gdal geotransform
    """
    try:
        ds = gdal.Open(pa)
    except RuntimeError, e:
        print "Unable to open raster from given path: " + str(pa)
        print e
        sys.exit()
        
    gt = ds.GetGeoTransform()
    del ds # delete link to file
    # Return x-y cellsize
    return ( gt[1] ,gt[5]*-1)
    
    
def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array,nodata = -9999, epsg=4326):
    """
    Creates a new raster based on
    newRasterfn = File and path name
    rasterOrigin = a tuple (width,height)
    pixelWidth and Heiht = cellsize
    array = the array
    """  
    
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    
    outband.WriteArray(array)
    
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(epsg)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    # Set nodata
    outband.SetNoDataValue(nodata)
    #flush
    outband.FlushCache()



def latlong2UTMzone(lon,lat):
    """
    Calculates the WGS84-UTM zone of a given combination of
    coordinates
    """
     
    # Normal calculation
    ZoneNumber = np.floor((lon + 180)/6) + 1
    
    # Special case for higher longitude levels
    if lat >= 56.0 and lat < 64.0 and lon >= 3.0 and lon < 12.0:
        ZoneNumber = 32
    # Special cases for svalbard
    if lat >= 72.0 and lat < 84.0:        
        if lon >= 0.0  and lon <  9.0:
            ZoneNumber = 31
        elif lon >= 9.0  and lon < 21.0:
            ZoneNumber = 33
        elif lon >= 21.0 and lon < 33.0:
            ZoneNumber = 35
        elif lon >= 33.0 and lon < 42.0:
            ZoneNumber = 37   
    
    return str( np.round(ZoneNumber,0).astype(int) )

def UTMis_northern(lat):
    """
    Determines if given latitude is a northern for UTM
    """
    if (lat < 0.0):
        return "south"
    else:
        return "north"


def wkt2proj4(wk):
    """
    Given an input WKT projection info
    - return the resulting proj4 string
    """
    # Get proj4 string    
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wk)
    return srs.ExportToProj4()

def length(x):
    """
    Short wrapper for length
    """
    return(len(x))
    
def returnListOfFiles(folder,ext=None):
    """
    Returns a list of all files in a folder.
    Optionally with a extension provided.
    """
    f = []
    for file in os.listdir(folder):
        if ext is not None:
            if file.endswith(ext):
                if path.isfile(file):
                    f = f.extend(file)
        else:
            if path.isfile(file):
                f = f.extend(file)
    return(f)