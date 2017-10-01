import pandas as pd
import numpy as np
import geopandas as gpd
pd.options.mode.chained_assignment = None

# FUNCTIONS SOURCED FROM 
# https://automating-gis-processes.github.io/Lesson5-interactive-map-Bokeh-advanced-plotting.html

def getXYCoords(geometry, coord_type):
    """ Returns either x or y coordinates from  geometry coordinate sequence. Used with LineString and Polygon geometries."""
    if coord_type == 'x':
        return geometry.coords.xy[0]
    elif coord_type == 'y':
        return geometry.coords.xy[1]

def getPolyCoords(geometry, coord_type):
    """ Returns Coordinates of Polygon using the Exterior of the Polygon."""
    ext = geometry.exterior
    return getXYCoords(ext, coord_type)
    
def getLineCoords(geometry, coord_type):
    """ Returns Coordinates of Linestring object."""
    return getXYCoords(geometry, coord_type)

def getPointCoords(geometry, coord_type):
    """ Returns Coordinates of Point object."""
    if coord_type == 'x':
        return geometry.x
    elif coord_type == 'y':
        return geometry.y
    
def multiGeomHandler(multi_geometry, coord_type, geom_type):
    """ 
    Function for handling multi-geometries. Can be MultiPoint, MultiLineString or MultiPolygon. 
    Returns a list of coordinates where all parts of Multi-geometries are merged into a single list. 
    Individual geometries are separated with np.nan which is how Bokeh wants them. 
    # Bokeh documentation regarding the Multi-geometry issues can be found here (it is an open issue)
    # https://github.com/bokeh/bokeh/issues/2321
    """
    
    for i, part in enumerate(multi_geometry):
        # On the first part of the Multi-geometry initialize the coord_array (np.array)
        if i == 0:
            if geom_type == "MultiPoint":
                coord_arrays = np.append(getPointCoords(part, coord_type), np.nan)
            elif geom_type == "MultiLineString":
                coord_arrays = np.append(getLineCoords(part, coord_type), np.nan)
            elif geom_type == "MultiPolygon":
                coord_arrays = np.append(getPolyCoords(part, coord_type), np.nan)
        else:
            if geom_type == "MultiPoint":
                coord_arrays = np.concatenate([coord_arrays, np.append(getPointCoords(part, coord_type), np.nan)])
            elif geom_type == "MultiLineString":
                coord_arrays = np.concatenate([coord_arrays, np.append(getLineCoords(part, coord_type), np.nan)])
            elif geom_type == "MultiPolygon":
                coord_arrays = np.concatenate([coord_arrays, np.append(getPolyCoords(part, coord_type), np.nan)])
    
    # Return the coordinates 
    return coord_arrays
    

def getCoords(row, geom_col, coord_type):
    """
    Returns coordinates ('x' or 'y') of a geometry (Point, LineString or Polygon) as a list (if geometry is LineString or Polygon). 
    Can handle also MultiGeometries.
    """
    # Get geometry
    geom = row[geom_col]
    
    # Check the geometry type
    gtype = geom.geom_type
    
    # "Normal" geometries
    # -------------------
    
    if gtype == "Point":
        return getPointCoords(geom, coord_type)
    elif gtype == "LineString":
        return list( getLineCoords(geom, coord_type) )
    elif gtype == "Polygon":
        return list( getPolyCoords(geom, coord_type) )
        
    # Multi geometries
    # ----------------
    
    else:
        return list( multiGeomHandler(geom, coord_type, gtype) ) 

# ---------------------

fp = r"vic-shapefile/LGA11aAust.shp"
aus = gpd.read_file(fp)
vic = aus[153:233]

crashes = pd.read_csv('crashes.csv')
counted = crashes.groupby("LGA_NAME").size()

crash_count = counted.to_frame()
vic["LGA_NAME11"] = vic["LGA_NAME11"].map(lambda x: x.split('(',1)[0])
vic["LGA_NAME11"] = vic["LGA_NAME11"].map(lambda x: x.upper())
vic["LGA_NAME11"] = vic["LGA_NAME11"].map(lambda x: x.rstrip())
vic["LGA_NAME11"] = vic["LGA_NAME11"].map(lambda x: x.replace("GREATER ",""))
vic["LGA_NAME11"] = vic["LGA_NAME11"].map(lambda x: x.replace("-"," "))

vic = vic.rename(columns = {"LGA_NAME11": "LGA_NAME"})

crash_count.index.name = "LGA_NAME"
crash_count.reset_index(inplace=True)

result = vic.merge(crash_count, on="LGA_NAME", how="left")
result = result.rename(columns = {0: "TOTAL_INCIDENTS"})

result.to_file('test.shp', driver="ESRI Shapefile")


result['x'] = result.apply(getCoords, geom_col='geometry', coord_type='x', axis=1)
result['y'] = result.apply(getCoords, geom_col='geometry', coord_type='y', axis=1)

from bokeh.models import ColumnDataSource

df = result.drop('geometry', axis=1).copy()
df = df.fillna('0')

source = ColumnDataSource(df)
