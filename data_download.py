
from conversions import norad2prn
from basics import SpaceVector
from satplots_logging import get_logger
import os
import requests
import json
from datetime import datetime, timedelta
import configparser
import pandas as pd
import numpy as np
from pathlib import Path
import shutil
from collections import Counter
from dotenv import load_dotenv
load_dotenv()


class TLE_element:
    def __init__(self, line1, line2, norad_id):
        self.line1 = line1
        self.line2 = line2
        self.norad_id = norad_id
        elems1 = line1.split()
        self.epoch = datetime(
            int("20"+elems1[3][:2]), 1, 1) + timedelta(days=float(elems1[3][2:]))


class Celestrak:
    ARCHIVE_PATH = "./downloads/celestrak"

    def __init__(self, config_file="./config/download_config.ini"):

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

    def download_tle(self, group):
        self.logger.info(f"Starting download for {group}.")
        req = requests.get(
            f"https://celestrak.com/NORAD/elements/gp.php?GROUP={group}&FORMAT=tle")

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
            new_date = datetime(
                int("20"+line.split()[3][:2]), 1, 1) + timedelta(days=float(line.split()[3][2:]))
            dates.append(new_date.date())

        date = Counter(dates).most_common(1)[0][0]
        date_str = datetime.strftime(date, "%Y%m%d")

        output_dir = Path(self.archive_path) / str(date.year) / \
                          str(date.month) / str(date.day)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"TLE_{date_str}_{group}.txt"

        tmp_file.replace(output_file)

    @classmethod
    def get_tles(cls, date, group=None):
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y/%m/%d")
        date_str = datetime.strftime(date, "%Y/%m/%d")
        date_str = datetime.strftime(date, "%Y%m%d")

        if not group:
            groups = ["galileo", "gps-ops", "glo-ops", "beidou"]
        else:
            groups = [group]

        result = []
        for group in groups:
            file_dir = Path(cls.ARCHIVE_PATH) / str(date.year) / \
                            str(date.month) / str(date.day) / \
                                f"TLE_{date_str}_{group}.txt"

            if not file_dir.exists() or file_dir.stat().st_size == 0:
                #raise Exception("TLE file does not exist or is empty")
                file_dir = Path(cls.ARCHIVE_PATH) / str(date.year) / \
                                str(date.month) / str(date.day) / \
                                    f"{date_str}_{group}.txt"
                if not file_dir.exists() or file_dir.stat().st_size == 0:
                    continue

            with file_dir.open('r') as f:
                lines = f.readlines()

            for i in range(0, len(lines), 3):
                new_tle = TLE_element(
                    lines[i+1], lines[i+2], lines[i].replace('\n', '').strip())
                result.append(new_tle)

        return result

    @classmethod
    def get_norad_ids(cls, date, group=None):
        result = []
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y/%m/%d-%H:%M:%S")
        indexes = [-2, -1, 0, 1, 2]
        dates = [date + timedelta(days=i) for i in indexes]
        for date in dates:
            tles = cls.get_tles(date, group)
            for tle in tles:
                if norad2prn(tle.norad_id):
                    result.append(tle.norad_id)

        return result

    @classmethod
    def get_prns(cls):
        filepath = Path("./tmp/prns.txt")
        if filepath.exists():
            with filepath.open("r") as f:
                lines = f.readlines()
            lines = [line.strip() for line in lines]
            return lines

        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = datetime.strftime(yesterday, "%Y/%m/%d")
        norad_ids = cls.get_norad_ids(yesterday_str)
        prns = []
        for norad_id in norad_ids:
            prn = norad2prn(norad_id)
            if prn:
                prns.append(prn)

        filepath.touch(exist_ok=True)
        with filepath.open("w") as f:
            for prn in prns:
                f.write(prn+"\n")

        return prns

    def download_all_csv(self):
        self.logger.info("Downloading all celestrak files")
        groups = self.config["CELESTRAK"]["groups"].split(",")
        for group in groups:
            self.download_csv(group)

    def download_csv(self, group):
        self.logger.info(f"Starting download for {group}.")
        req = requests.get(
            f"https://celestrak.com/NORAD/elements/gp.php?GROUP={group}&FORMAT=csv")

        tmp_dir = Path(self.tmp_path)
        tmp_file = tmp_dir / "celestrak_tmp.csv"
        tmp_file.touch()
        tmp_file.write_text(req.text)

        df = pd.read_csv(tmp_file)
        epochs = [epoch.date() for epoch in pd.to_datetime(df.EPOCH)]
        date = Counter(epochs).most_common(1)[0][0]
        date_str = datetime.strftime(date, "%Y%m%d")

        output_dir = Path(self.archive_path) / str(date.year) / \
                          str(date.month) / str(date.day)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{date_str}_{group}.csv"

        tmp_file.replace(output_file)

    @classmethod
    def get_csv(cls, date, group):
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y/%m/%d")
        date_str = datetime.strftime(date, "%Y/%m/%d")

        date_str = datetime.strftime(date, "%Y%m%d")
        file_dir = Path(cls.ARCHIVE_PATH) / str(date.year) / \
                        str(date.month) / str(date.day) / \
                            f"{date_str}_{group}.csv"

        if not file_dir.exists() or file_dir.stat().st_size == 0:
            return pd.DataFrame

        df = pd.read_csv(file_dir, parse_dates=['EPOCH'])
        return df


class IGS:
    @classmethod
    def get_stations_df(cls):
        tmp_file = Path("./tmp/IGS_stations.csv")
        if not tmp_file.exists():
            req = requests.get(
                "https://files.igs.org/pub/station/general/IGSNetwork.csv")
            tmp_file.write_text(req.text)
        df = pd.read_csv(tmp_file)
        df.rename(columns={"#stn": "StationFull"}, inplace=True)
        df["Station"] = df.StationFull.apply(lambda x: x[:4])

        return df

    @classmethod
    def get_IGS_stations_df_full(cls):
        df = cls.get_stations_df()
        Xs = list(df.X)
        Ys = list(df.Y)
        Zs = list(df.Z)
        lats = []
        lons = []
        for i in range(len(Xs)):
            new_pos = SpaceVector(Xs[i], Ys[i], Zs[i], skip_llh=False)
            lats.append(new_pos.lat)
            lons.append(new_pos.lon)

        new_df = pd.DataFrame(zip(lats, lons), columns=["lat", "lon"])
        result_df = pd.concat([df, new_df], axis=1)

        return result_df

    @classmethod
    def get_IGS_station_list(cls):
        return list(pd.unique(cls.get_stations_df().Station))


class Nasa:
    API_KEY = os.getenv('NASA_API_KEY')
    ARCHIVE_PATH = "./downloads/NASA"

    @classmethod
    def download_APOD(cls, date=None):
        if not date:
            date = datetime.now().date()
        year = str(date.year)
        month = str(date.month).zfill(2)
        day = str(date.day).zfill(2)

        req = requests.get(
            f"https://api.nasa.gov/planetary/apod?date={year}-{month}-{day}&api_key={cls.API_KEY}")
        resp_json = json.loads(req.text)

        if 'media_type' in resp_json and resp_json['media_type'] == 'image':
            json_file_dir = Path(cls.ARCHIVE_PATH) / year / month / day
            json_file_dir.mkdir(parents=True, exist_ok=True)
            json_file = json_file_dir / f"{year}_{month}_{day}.json"

            image_file_dir = Path(cls.ARCHIVE_PATH) / year / month / day
            image_file_dir.mkdir(parents=True, exist_ok=True)
            image_file = image_file_dir / f"{year}_{month}_{day}.jpg"

            with json_file.open('w') as f:
                json.dump(resp_json, f)

            img_data = requests.get(resp_json['url']).content
            with image_file.open('wb') as f:
                f.write(img_data)

    @classmethod
    def get_APOD_dates(cls):
        dates = []
        for _, _, files in os.walk(cls.ARCHIVE_PATH, topdown=False):
            for name in files:
                #print("File: ",os.path.join(root, name))
                dates.append("/".join(name.split(".")[0].split("_")))
        dates = list(set(dates))

        return sorted(dates)

