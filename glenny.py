
import re
import requests
from datetime import date,datetime

from data_download import Celestrak,IGS
from geometry import Geometry
'''
cel = Celestrak()
cel.download_all_tles()
'''
geom = Geometry()
norad_id = "GSAT0215 (PRN E21)"
start = date(2020,12,26)
end = date(2020,12,27)
geom.load_tles_celestrak("galileo",start,end)
epoch = datetime(2020,12,26,12,0,0)
sat_pos = geom.get_sat_pos(norad_id,epoch)
geom.load_IGS_stations()
stat_pos = geom.get_station_pos("ABMF")
#print(pos.get_elevation(stat_pos,sat_pos))

start = "2020/12/25-00:00:00"
end = "2020/12/27-00:00:00"
df = geom.get_stations_in_view_sat_track(norad_id,start,end)
print(df)


