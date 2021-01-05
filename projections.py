'''
Basic geometry projections
'''
import numpy as np
import pyproj

def ecef2latlonheight(x,y,z):
    '''
    returns tuple : (lat,lon,height)
    '''
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    lon, lat, alt = pyproj.transform(ecef, lla, x, y, z, radians=False)
    #alt_geom = np.linalg.norm([x,y,z])
    #print("Glenny alt geom:",alt_geom)
    #print("Glenny alt proj:",alt)
    return (lat,lon,alt)

def latlonheight2ecef(lat,lon,alt):
    '''
    returns tuple : (x,y,z)
    '''
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    x,y,z = pyproj.transform(lla, ecef, lon, lat, alt, radians=False)
    return (x,y,z)
