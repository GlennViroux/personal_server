
import argparse
from pathlib import Path
from datetime import datetime

from data_download import Celestrak,IGS
from geometry import Geometry
from conversions import GlonassInfo
from snippets import df2geojsonLineString,df2geojsonSatPoints,df2geojsonStationPoints,df2timeseriesdata

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--download_tles',action="store_true",help="Activate this option in order to download the latest TLEs available on Celestrak.")
    parser.add_argument('-v','--download_csv',action="store_true",help="Activate this option in order to download the latest CSV files available on Celestrak.")
    parser.add_argument('-g','--download_glonass_info',action="store_true",help="Activate this option in order to download the latest CUS message from the Glonass website.")
    parser.add_argument('-c','--calculate',action="store_true",help="Calculate data necessary for plotting.")
    parser.add_argument('-s','--start',help="Start date.")
    parser.add_argument('-e','--end',help="End date.")
    parser.add_argument('-n','--norad_ids',help="List of norad IDs. If not provided, results are calculated for all available spacecraft.")

    args = parser.parse_args()

    celestrak = Celestrak()
    if args.download_tles:
        celestrak.download_all_tles()

    if args.download_csv:
        celestrak.download_all_csv()

    if args.download_glonass_info:
        GlonassInfo.download_cus_message()

    if args.calculate:
        start = datetime.strptime(args.start,"%Y/%m/%d-%H:%M:%S")
        end = datetime.strptime(args.end,"%Y/%m/%d-%H:%M:%S")
        start_date = start.date()
        end_date = end.date()

        geom = Geometry()
        geom.load_IGS_stations()
        geom.load_tles_celestrak(start_date,end_date)
        df_stations = IGS.get_IGS_stations_df_full()
        basepath = Path("./output") / str(start_date.year) / str(start_date.month).zfill(2) / str(start_date.day).zfill(2)
        basepath.mkdir(parents=True,exist_ok=True)
        df2geojsonStationPoints(df_stations,basepath / "stations")
        geom.calculate_all(start,end,args.norad_ids)


