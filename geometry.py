'''
Positions manager class
'''
import pytz
import math
import pandas as pd
import datetime
import configparser
from pathlib import Path
from skyfield.api import EarthSatellite,load

from data_download import Celestrak,IGS
from basics import SpaceVector
from satplots_logging import get_logger

EARTH_FLATTE_GRS80 = 1.0/298.257222101

class Geometry:
    def __init__(self,config_file="./config/config.ini"):

        conf_file = Path(config_file)
        if not conf_file.exists():
            raise Exception(f"Configuration file {config_file} does not exist, exiting.")
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        log_file = "./logs/geometry_log.txt"
        self.logger = get_logger(log_file)
        
        self.ts = load.timescale()
        self.tles_df = pd.DataFrame.from_dict({"norad_id":[],"epoch":[],"line1":[],"line2":[]})
        self.igs_stations_df = pd.DataFrame.from_dict({"Station":[],"StationFull":[],"X":[],"Y":[],"Z":[],"ReceiverName":[],"AntennaName":[],"ClockType":[]})

    def load_tles_celestrak(self,group,start,end):
        self.logger.info("Loading TLEs from Celestrak")
        if not isinstance(start,datetime.date):
            raise Exception("Funcion load_tles_celestrak: No date object provided")
        if not isinstance(end,datetime.date):
            raise Exception("Funcion load_tles_celestrak: No date object provided")

        tle_start = start - datetime.timedelta(days=14)
        tle_end = end + datetime.timedelta(days=14)
        dates = pd.date_range(tle_start,tle_end)

        for date in dates:
            tles = Celestrak.get_tles(date,group)
            if not tles:
                continue
            df_dict = {"norad_id":[],"epoch":[],"line1":[],"line2":[]}
            for tle in tles:
                df_dict["norad_id"].append(tle.norad_id)
                df_dict["epoch"].append(tle.epoch)
                df_dict["line1"].append(tle.line1)
                df_dict["line2"].append(tle.line2)
            new_df = pd.DataFrame.from_dict(df_dict)
            self.tles_df = pd.concat([self.tles_df,new_df])

    def load_IGS_stations(self):
        self.logger.info("Loading IGS stations")
        self.igs_stations_df = IGS.get_stations_df()

    def get_closest_tle(self,norad_id,epoch):
        '''
        Return the closest (epoch-wise) tle that is loaded.
        '''
        self.logger.debug(f"Getting closest TLE for {norad_id} and {epoch}")
        if isinstance(epoch,str):
            epoch = datetime.datetime.strptime(epoch,"%Y/%m/%d-%H:%M:%S")
        if not isinstance(epoch,datetime.datetime):
            raise Exception("Bad epoch provided, fix it")

        df = self.tles_df[self.tles_df.norad_id==norad_id]
        if df.empty:
            raise Exception(f"No valid TLE found for {norad_id} and {epoch}")

        epoch_diff = (df.epoch - epoch).apply(lambda x: abs(x.total_seconds())).rename("epoch_diff")
        df = pd.concat([df,epoch_diff],axis=1)
        df.sort_values("epoch_diff",inplace=True)
        return df.iloc[0]
      
    def get_sat_pos(self,norad_id,epoch):
        self.logger.debug(f"Getting position for {norad_id} and {epoch}")
        if isinstance(epoch,str):
            epoch = datetime.datetime.strptime(epoch,"%Y/%m/%d-%H:%M:%S")

        tle = self.get_closest_tle(norad_id,epoch)
        satellite = EarthSatellite(tle.line1, tle.line2, tle.norad_id, self.ts)

        timezone = pytz.timezone("UTC")
        epoch_aware = timezone.localize(epoch)
        t = self.ts.from_datetime(epoch_aware)
        geocentric = satellite.at(t)
        subpoint = geocentric.subpoint()
        ecef = geocentric.position.m

        return SpaceVector(
            x=ecef[0],
            y=ecef[1],
            z=ecef[2],
            lat=subpoint.latitude.degrees,
            lon=subpoint.longitude.degrees)

    def get_sat_positions(self,norad_id,start,end,sampling=5):
        self.logger.info(f"Getting all positions for {norad_id} between {start} and {end}")
        if isinstance(start,str):
            start = datetime.datetime.strptime(start,"%Y/%m/%d-%H:%M:%S")
        if isinstance(end,str):
            end = datetime.datetime.strptime(end,"%Y/%m/%d-%H:%M:%S")
        
        if not isinstance(start,datetime.datetime):
            raise Exception("Funcion get_sat_positions: No datetime object provided for start")
        if not isinstance(end,datetime.datetime):
            raise Exception("Funcion get_sat_positions: No datetime object provided for end")
        if not isinstance(sampling,int):
            raise Exception("Funcion get_sat_positions: No int object provided for sampling")


        number_of_epochs = (end-start)/datetime.timedelta(minutes=sampling)
        epochs = [(start + datetime.timedelta(minutes=sampling*i)) for i in range(int(number_of_epochs))]
        positions = []
        for epoch in epochs:
            positions.append(self.get_sat_pos(norad_id,epoch))
        
        df = pd.DataFrame(zip(epochs,positions),columns=["epoch","pos"])

        return df

    def get_station_pos(self,station):
        self.logger.debug(f"Getting position for station {station}")
        res = self.igs_stations_df[self.igs_stations_df.Station==station]
        if len(res)==0:
            raise Exception(f"No station data was found for station: {station}")

        result = SpaceVector(res.iloc[0].X,res.iloc[0].Y,res.iloc[0].Z)

        return result

    def get_elevation(self,station_pos,sat_pos):
        self.logger.debug(f"Getting elevation between station at {station_pos} and satetllite at {sat_pos}")
        if not isinstance(station_pos,SpaceVector):
            raise Exception("Provided station position is not a SpaceVector.")
        if not isinstance(sat_pos,SpaceVector):
            raise Exception("Provided satellite position is not a SpaceVector.")

        station_to_sat = sat_pos - station_pos
        distance = station_to_sat.norm()
        station_normal = station_pos
        station_normal.z /= ((1.0 - EARTH_FLATTE_GRS80) * (1.0 - EARTH_FLATTE_GRS80))
        aux_norm = station_normal.norm()
        aux = station_to_sat.dot(station_normal)

        if aux_norm*distance<1e-10:
            return 0

        sinE = aux/(aux_norm * distance)
        elev = math.degrees(math.asin(sinE))

        return elev 

    def get_stations_in_view(self,sat_pos):
        self.logger.debug(f"Getting stations in view for satellite at {sat_pos}")
        elev_mask = float(self.config["general"]["elevation_mask"])
        stations = [stat.upper() for stat in self.config["general"]["stations"].split(",")]
        stations_in_view = []
        for station in stations:
            stat_pos = self.get_station_pos(station)
            elevation = self.get_elevation(stat_pos,sat_pos)
            if elevation>=elev_mask:
                stations_in_view.append(station)

        return stations_in_view

    def get_stations_in_view_sat_track(self,norad_id,start,end):
        self.logger.info(f"Getting stations in view along the track fro {norad_id} between {start} and {end}")
        sat_pos_df = self.get_sat_positions(norad_id,start,end)
        stations_in_view = []
        number_stats_in_view = []
        for _,row in sat_pos_df.iterrows():
            sat_pos = row.pos
            stats_in_view = self.get_stations_in_view(sat_pos)
            stations_in_view.append(stats_in_view)
            number_stats_in_view.append(len(stats_in_view))

        new_df = pd.DataFrame(zip(number_stats_in_view,stations_in_view),columns=["number_stations_in_view","stations_in_view"])

        df = pd.concat([sat_pos_df,new_df],axis=1)

        return df



        



