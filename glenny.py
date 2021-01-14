
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
'''
Nasa.get_APOD_dates()


