# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 15:42:37 2020

@author: 18120900
"""
import arcpy
from arcpy import env
from arcpy.sa import *


field = ["Code","wgsLongitu","wgsLatitud"]
openFilePath = "F:/18120900/Documents/ArcGIS/0 shape文件/北京市GIS文件"
for i in range(3):
    env.workspace = openFilePath
    saveFilePatn = "F:/18120900/Documents/ArcGIS/0 shape文件/Output/" + str(i+1)
    name = KernelDensity("CrossRoad-Data2", field[i], 0.001, 0.03, "SQUARE_KILOMETERS")
    name.save(saveFilePatn)