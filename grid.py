import math

class Grid:

    @classmethod
    def get_plane_grid(cls,number_of_points=1200,height=0):
        '''
        get grid as a list of tuples: [(lat0,lon0,0),(lat1,lon1,0),...]
        '''
        interval_lon = int(360/math.sqrt(number_of_points)-1)
        interval_lat = int(180/math.sqrt(number_of_points)-1)
        grid = []
        lats = list(range(-90,90,interval_lat))+[90]
        lons = list(range(0,360,interval_lon))+[360]
        for current_lat in lats:
            for current_lon in lons:
                grid.append((current_lat,current_lon,height))

        return grid,lats,lons