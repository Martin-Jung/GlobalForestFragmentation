# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 13:31:14 2016

@author: Martin Jung
"""

import rasterio
import numpy as np

# System modules
import os
from os import path
from glob import glob
import subprocess

# Custom Module
from functions import *
from metrics import calcMetrics

##################
#------------------
##################
m = "Patch density"
# Other Parameter
spacing = 10
y = 2015
print "Processing the year " + str(y)
# Set working dir
os.chdir("ALOS_PALSAR/%s/" % (str(y)) )

output = "%s_%s_%s/" % (m.replace(" ","_"),str(y),str(spacing) )
if path.exists(output) == False:
    print "Creating folder: " + output
    os.mkdir(output)

# Get list
ll = glob("./"+"*.tar.gz")
for ar in ll:
    # Untar
    untar(ar,"FNF")
    # -----------------------------------------------#
    # Get list of hdr
    l = glob("FNF/"+"*.hdr")
    # Take header name from here and process
    for ras in l:
        # Get raster file name
        pa = path.splitext(ras)[0]
        
        # Test if file in extract exists, otherwise skip
        if path.exists(pa) == False:
            continue
        
        # Test if file was already computed
        o = output + path.basename(pa)+".tif"
        if path.exists(o) == True:
            continue
        # Process
        ####    
        # Register GDAL drivers:
        with rasterio.drivers():
            
            # Read raster as array
            with rasterio.open(pa) as src:
                # Query metadata
                width = src.width
                height = src.height
                nodata = src.nodatavals
                crs = src.crs 
                crs_wkt = src.crs_wkt
                affine = src.affine
                profile = src.profile
                transform = src.transform  
                              
                if src.closed == False:
                    src.close()
        
            # Create coordinate vector
            nx, ny = (spacing+1, spacing+1)
            x = np.linspace(0, width, nx)
            y = np.linspace(0, height, ny)
            # Round just to be sure
            x = np.array([ np.round(elem, 0) for elem in x ] )      
            y = np.array([ np.round(elem, 0) for elem in y ] )      
        
            print "Processing File %s" % path.basename(pa)
            
            # Create a result array
            result = np.empty([spacing,spacing])
            
            # Processing
            for row in range(spacing):
                # Column
                for col in range(spacing):
                    # ((row_start, row_stop), (col_start, col_stop))
                    window = (x[row],x[row+1]), (y[col],y[col+1])
                    # Read part of array in
                    with rasterio.open(pa) as src:        
                        array = src.read(1, window = window )
                        src.close()
                    # --- #            
                    # Set the cellsize (assumed to be uniform for ALOS PALSAR)
                    cs = 25            
                    classes = np.unique(array)
                    
                    # Object
                    cm = calcMetrics(array,cs,classes)
                    
                    # Set everything other than forest to -1            
                    cl_array = np.copy(array).astype("float")
                    cl_array[cl_array!=1] = 0            
                    cm.f_ccl(cl_array) # CC-labeling
                    
                    # Execute computation
                    name, value = cm.execSingleMetric(m, 1)
                    
                    # Finally write the result into the array
                    result[row,col] = value
                    
                    # Clean up
                    del array
                    del cm
                    
                    
            
            # Calculate resulting sample size
            col, row = x[0], y[0]
            x1,y1 = src.affine * (col, row)
            col, row = x[1], y[1]
            x2,y2 = src.affine * (col, row)        
            # Subtract and get new cell-size in current projection
            transform[1] = x2 - x1
            transform[5] = y2 - y1
        
            # Take the same origin
            col, row = 0, 0
            yo, xo = src.affine * (col, row)
            # output file
            out = path.join("FNF",path.basename(pa) +".tif")
            
            # Update the original profile
            profile.update(
                dtype=rasterio.float64,
                driver= 'GTiff', # Gtiff output
                count=1, # one band
                compress='lzw', # with compression
                nodata = -9999, # new nodata
                transform = transform, # corrected transform
                width = result.shape[0], # new width
                height = result.shape[1] # new height
                )
            # Finally write the result   
            with rasterio.open(out, 'w', **profile) as dst:
                dst.write(result.astype(rasterio.float64), 1)
    
    # Create a VRT of the result
    com = ["gdalbuildvrt","-overwrite",output+"out.vrt"]
    for myfile in glob("FNF/*.tif"):
       com.append(myfile)
    try:
        subprocess.call(com)
    except OSError:
        print "Gdalbuildvrt or file could not be found"
    
    # Merge all output files into a single one
    com = ["gdal_translate","-of","Gtiff","-co","COMPRESS=LZW",output+"out.vrt",output + path.basename(pa)+".tif"]
    try:
        subprocess.call(com)
    except OSError:
        print "Something went wrong during merging"
    
    # Delete the VRT
    try:
        os.remove(output+"out.vrt")
    except OSError:
        print "Could not find out.vrt"
    
    try:
        deleteDir("FNF")
    except OSError:
        print "Extraction Archive already deleted or something went wrong"

print "Done!"
