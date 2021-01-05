'''
Basic class definitions
'''
import numpy as np
from projections import ecef2latlonheight,latlonheight2ecef

class SpaceVector:
    def __init__(self,x,y,z,lat=None,lon=None,height=None,skip_llh=True):
        self.x = x
        self.y = y
        self.z = z

        if (not lat or not lon or not height) and not skip_llh:
            self.lat = None
            self.lon = None
            self.height = None
            self.lat,self.lon,self.height = self.to_llh()
        else:
            self.lat = lat
            self.lon = lon
            self.height = height

    def __add__(self,other):
        x_add = self.x + other.x
        y_add = self.y + other.y
        z_add = self.z + other.z
        return SpaceVector(x_add,y_add,z_add)

    def __sub__(self,other):
        x_sub = self.x - other.x
        y_sub = self.y - other.y
        z_sub = self.z - other.z
        return SpaceVector(x_sub,y_sub,z_sub)

    def __truediv__(self,other):
        return SpaceVector(self.x/other,self.y/other,self.z/other)

    def __mul__(self,other):
        return SpaceVector(self.x*other,self.y*other,self.z*other)

    def __str__(self):
        return "({},{},{})".format(self.x,self.y,self.z)

    def __repr__(self):
        return str(self)

    def norm(self):
        return np.linalg.norm([self.x,self.y,self.z])

    def dot(self,other):
        return self.x*other.x+self.y*other.y+self.z*other.z

    def to_llh(self):
        if self.lat and self.lon and self.height:
            return (self.lat,self.lon,self.height)
        else:
            return ecef2latlonheight(self.x,self.y,self.z)

    @classmethod
    def from_llh(cls,lat,lon,height):
        x,y,z = latlonheight2ecef(lat,lon,height)
        return SpaceVector(x,y,z,lat,lon,height)

    