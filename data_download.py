
import requests
from datetime import datetime,timedelta
import configparser
import pandas as pd
import numpy as np
from pathlib import Path
import shutil
from collections import Counter

from satplots_logging import get_logger

class TLE_element:
    def __init__(self,line1,line2,norad_id):
        self.line1 = line1
        self.line2 = line2
        self.norad_id = norad_id
        elems1 = line1.split()
        self.epoch = datetime(int("20"+elems1[3][:2]),1,1) + timedelta(days=float(elems1[3][2:]))


class Celestrak:
    ARCHIVE_PATH = "./downloads/celestrak"
    def __init__(self,config_file="./config/download_config.ini"):
        
        self.tmp_path = "./tmp/"
        self.archive_path = "./downloads/celestrak"

        log_file = "./logs/celestrak_download_log.txt"
        self.logger = get_logger(log_file)
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def download_all_tles(self):
        self.logger.info("Downloading all TLE celestrak files")
        groups = self.config["CELESTRAK"]["groups"].split(",")
        for group in groups:
            self.download_tle(group)

    def download_tle(self,group):
        self.logger.info(f"Starting download for {group}.")
        req = requests.get(f"https://celestrak.com/NORAD/elements/gp.php?GROUP={group}&FORMAT=tle")

        tmp_dir = Path(self.tmp_path)
        tmp_file = tmp_dir / "celestrak_tmp.csv"
        tmp_file.touch()
        tmp_file.write_text(req.text)

        dates = []
        with tmp_file.open() as f:
            lines = f.readlines()
        for line in lines:
            if not line.startswith("1 "):
                continue
            new_date = datetime(int("20"+line.split()[3][:2]),1,1) + timedelta(days=float(line.split()[3][2:]))
            dates.append(new_date.date())

        date = Counter(dates).most_common(1)[0][0]
        date_str = datetime.strftime(date,"%Y%m%d")
        
        output_dir = Path(self.archive_path) / str(date.year) / str(date.month) / str(date.day)
        output_dir.mkdir(parents=True,exist_ok=True)
        output_file = output_dir / f"TLE_{date_str}_{group}.txt"

        tmp_file.replace(output_file)

    @classmethod
    def get_tles(cls,date,group):
        if isinstance(date,str):
            date = datetime.strptime(date,"%Y/%m/%d")
        date_str = datetime.strftime(date,"%Y/%m/%d")

        date_str = datetime.strftime(date,"%Y%m%d")
        file_dir = Path(cls.ARCHIVE_PATH) / str(date.year) / str(date.month) / str(date.day) / f"TLE_{date_str}_{group}.txt"

        if not file_dir.exists() or file_dir.stat().st_size==0:
            return []

        with file_dir.open('r') as f:
            lines = f.readlines()
        
        result = []
        for i in range(0,len(lines),3):
            new_tle = TLE_element(lines[i+1],lines[i+2],lines[i].replace('\n','').strip())
            result.append(new_tle)

        return result
        
    def download_all_csv(self):
        self.logger.info("Downloading all celestrak files")
        groups = self.config["CELESTRAK"]["groups"].split(",")
        for group in groups:
            self.download_csv(group)

    def download_csv(self,group):
        self.logger.info(f"Starting download for {group}.")
        req = requests.get(f"https://celestrak.com/NORAD/elements/gp.php?GROUP={group}&FORMAT=csv")

        tmp_dir = Path(self.tmp_path)
        tmp_file = tmp_dir / "celestrak_tmp.csv"
        tmp_file.touch()
        tmp_file.write_text(req.text)

        df = pd.read_csv(tmp_file)
        epochs = [epoch.date() for epoch in pd.to_datetime(df.EPOCH)]
        date = Counter(epochs).most_common(1)[0][0]
        date_str = datetime.strftime(date,"%Y%m%d")
        
        output_dir = Path(self.archive_path) / str(date.year) / str(date.month) / str(date.day)
        output_dir.mkdir(parents=True,exist_ok=True)
        output_file = output_dir / f"{date_str}_{group}.csv"

        tmp_file.replace(output_file)

    @classmethod
    def get_csv(cls,date,group):
        if isinstance(date,str):
            date = datetime.strptime(date,"%Y/%m/%d")
        date_str = datetime.strftime(date,"%Y/%m/%d")

        date_str = datetime.strftime(date,"%Y%m%d")
        file_dir = Path(cls.ARCHIVE_PATH) / str(date.year) / str(date.month) / str(date.day) / f"{date_str}_{group}.csv"

        if not file_dir.exists() or file_dir.stat().st_size==0:
            return pd.DataFrame

        df = pd.read_csv(file_dir,parse_dates=['EPOCH'])
        return df

class IGS:
    @classmethod
    def get_stations_df(cls):
        req = requests.get("https://files.igs.org/pub/station/general/IGSNetwork.csv")
        tmp_file = Path("./tmp/IGS_stations.csv")
        tmp_file.write_text(req.text)
        df = pd.read_csv(tmp_file)
        df.rename(columns={"#stn":"StationFull"},inplace=True)
        df["Station"] = df.StationFull.apply(lambda x : x[:4])

        return df




