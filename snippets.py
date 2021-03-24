
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import pandas as pd 
import json
import geojson
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

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

def send_mail(mail_from,name,text):
    '''
    Send a mail using the Sendgrid API
    '''
    message = Mail(
        from_email='portfolioglennviroux@gmail.com',
        to_emails='glenn.viroux@gmail.com',
        subject=f"Mail from {name} - {mail_from}",
        html_content=f"<p>{text}</p>"
    )

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response)
    except Exception as e:
        print(e)

def get_apod(year,month,day,what):
    '''
    Get the apod for the provided date.
    '''
    if what=='json':
        apod_json = None
        json_file = Path(f"./downloads/NASA/{year}/{month}/{day}/{year}_{month}_{day}.json")
        if json_file.exists():
            with json_file.open('r') as f:
                apod_json = json.load(f)
        return apod_json

    elif what=="image":
        apod_image = f"./downloads/NASA/{year}/{month}/{day}/{year}_{month}_{day}.jpg"
        if not Path(apod_image).exists():
            return False
        return apod_image

def write_to_file(df:pd.DataFrame,filepath,filename):
    '''
    Write the dataframe to the given output file.
    '''

    filepath = Path(filepath)
    filepath.mkdir(parents=True,exist_ok=True)

    output = filepath / filename
    write_header = True
    if output.exists() and output.stat().st_size>0:
        write_header = False

    df.to_csv(output,header=write_header,mode='a',index=False)


