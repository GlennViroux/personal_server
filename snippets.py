
import pandas as pd 
import json
import geojson
from pathlib import Path
from datetime import datetime

def df2geojsonSatPoints(df:pd.DataFrame,basepath):
    '''
    Convert the df (with columns: epoch,lat,lon,number_stations_in_view and stations_in_view)
    to geoJSON format.
    '''
    for prn in pd.unique(df.prn):
        features = []
        insert_features = lambda x: features.append(
            geojson.Feature(
                geometry=geojson.Point(coordinates=[x["lon"],x["lat"]]),
                properties={
                    "prn":x["prn"],
                    "epoch":datetime.strftime(x["epoch"],"%Y/%m/%d-%H:%M:%S"),
                    "number_stations_in_view":x["number_stations_in_view"],
                    "stations_in_view":" ".join(x["stations_in_view"])
                }
            )
        )
        df[df.prn==prn].apply(insert_features,axis=1)
        basepath = Path(basepath)
        basepath.mkdir(parents=True,exist_ok=True)
        filename = prn+".json"
        output = Path(basepath) / filename
        with output.open("w") as f:
            geojson.dump(geojson.FeatureCollection(features),f,sort_keys=True, ensure_ascii=False)

def df2geojsonStationPoints(df:pd.DataFrame,basepath):
    '''
    Convert the df to geoJSON format.
    '''
    features = []
    insert_features = lambda x: features.append(
        geojson.Feature(
            geometry=geojson.Point(coordinates=[x["lon"],x["lat"]]),
            properties={
                "station":x["Station"],
                "receiver":x["ReceiverName"],
                "antenna":x["AntennaName"],
                "clock":x["ClockType"]
            }
        )
    )

    df.apply(insert_features,axis=1)
    basepath = Path(basepath)
    basepath.mkdir(parents=True,exist_ok=True)
    output = basepath / "stations.json"
    with output.open("w") as f:
        geojson.dump(geojson.FeatureCollection(features),f,sort_keys=True, ensure_ascii=False)

def df2geojsonLineString(df:pd.DataFrame,basepath):
    '''
    Convert the df (with columns: epoch,lat,lon,number_stations_in_view and stations_in_view)
    to geoJSON format.
    '''
    for prn in pd.unique(df.prn):
        coordinates = []
        add_coordinates = lambda x: coordinates.append([x["lon"],x["lat"]])
        df[df.prn==prn].apply(add_coordinates,axis=1)

        features = [geojson.Feature(
            geometry=geojson.LineString(coordinates=coordinates),
            properties={"prn":prn}
        )]
        #print(df[df.prn==prn])
        
        basepath = Path(basepath)
        basepath.mkdir(parents=True,exist_ok=True)
        filename = prn+".json"
        output = basepath / filename
        with output.open("w") as f:
            geojson.dump(geojson.FeatureCollection(features),f,sort_keys=True,ensure_ascii=False)

def df2timeseriesdata(df:pd.DataFrame,basepath):

    '''
    Convert the df to JSON format ready to be read by the TS files.
    '''
    for prn in pd.unique(df.prn):
        data = []
        add_data = lambda x : data.append(
            {
                "epoch":datetime.strftime(x["epoch"],"%Y/%m/%d-%H:%M:%S"),
                "stations":x["number_stations_in_view"]
            }
        )

        df[df.prn==prn].apply(add_data,axis=1)

        basepath = Path(basepath)
        basepath.mkdir(parents=True,exist_ok=True)
        filename = prn+".json"
        output = basepath / filename
        with output.open("w") as f:
            json.dump(data,f)

def check_output(product,date,sat=None):
    '''
    Check if output exists for the provided product, date and 
    satellite (if applicable).
    '''
    year = str(date.year)
    month = str(date.month).zfill(2)
    day = str(date.day).zfill(2)
    filepath = Path(f"./output/{year}/{month}/{day}/{product}")
    if sat:
        filepath = filepath / f"{sat}.json"
    else:
        filepath = filepath / f"{product}.json"

    if filepath.exists() and filepath.stat().st_size>0:
        return True
    return False

