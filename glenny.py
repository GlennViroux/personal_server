
import re
import requests
from datetime import date,datetime

from data_download import Celestrak,IGS
from geometry import Geometry
from snippets import df2geojsonLineString,df2geojsonSatPoints,df2geojsonStationPoints,df2timeseriesdata
'''
cel = Celestrak()
cel.download_all_tles()
'''
geom = Geometry()
norad_id = "GSAT0215 (PRN E21)"
start = date(2020,12,26)
end = date(2020,12,27)
geom.load_tles_celestrak(start,end)
epoch = datetime(2020,12,25,9,45,0)
#sat_pos = geom.get_sat_pos(norad_id,epoch)
geom.load_IGS_stations()

#geom.plot_elevations(sat_pos)

start = "2021/01/03-00:00:00"
end = "2021/01/03-00:10:00"
df = geom.calculate_all(start,end)
df_stations = IGS.get_IGS_stations_df_full()
print(df)

output_file = "./output/output_satpoints.json"
df2geojsonSatPoints(df,output_file)
output_file = "./output/output_sattrack.json"
df2geojsonLineString(df,output_file)
output_file = "./output/output_stations.json"
df2geojsonStationPoints(df_stations,output_file)
output_file = "./output/timeseries.json"
df2timeseriesdata(df,output_file)



