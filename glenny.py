
import re
import requests
from datetime import date,datetime,timedelta

from data_download import Celestrak,IGS,Nasa
from geometry import Geometry
from snippets import df2geojsonLineString,df2geojsonSatPoints,df2geojsonStationPoints,send_mail

'''
start = datetime.strptime('2021/01/10',"%Y/%m/%d")
end = datetime.now()
diff = int((end-start)/timedelta(days=1))
print(diff)
dates = [(start+timedelta(days=i)).date() for i in range(diff)]
for date in dates:
    print(date)
    Nasa.download_APOD(date)
Nasa.get_APOD_dates()
'''
geom = Geometry()
norad_id = "BEIDOU-3 M24 (C46),GSAT0202 (PRN E14)"
start = "2021/01/25-00:00:00"
end = "2021/01/26-00:10:00"
start_date = date(2021,1,15)
end_date = date(2021,1,16)
geom.load_tles_celestrak(start_date,end_date)
geom.load_IGS_stations()
geom.calculate_all(start,end,norad_id)
