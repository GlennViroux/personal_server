import io
import flask
import json
import tempfile
import subprocess
import time
import pandas as pd
from pathlib import Path
from datetime import datetime,timedelta
from flask import jsonify,request,abort,send_file
from flask_cors import CORS

from data_download import Celestrak,IGS,Nasa
from conversions import norad2prn
from snippets import send_mail,get_apod
from file_utils import get_temp_file
from music_classification import MusicClassification,MusicConfig

app = flask.Flask(__name__)
app.config["DEBUG"] = False
CORS(app)

cors = CORS(app,resources={
    "r/*":{
        "origins":"*"
    }
})

@app.before_first_request
def load_model_to_app():
    config_file = "./machine_learning/model_results/results_36/model_config.txt"
    config = MusicConfig.read_config(config_file)
    mclas = MusicClassification(config)
    mclas.load_saved_model(36)

    app.mclas = mclas

@app.route('/servercheck',methods=["GET"])
def check_server():
    return jsonify({"message":"ok!"})

@app.route('/prns',methods=["GET"])
def get_prns():
    prns = Celestrak.get_prns()
    return jsonify(prns)

@app.route('/stations',methods=["GET"])
def get_stations():
    result = IGS.get_IGS_station_list()
    return jsonify(result)

@app.route('/earth',methods=["GET"])
def get_earth_data():
    filepath = Path("./tmp/earth-data.json")
    result = {}
    with filepath.open("r") as f:
        result = json.load(f)

    return jsonify(result)

@app.route('/check',methods=["GET"])
def check_data():
    '''
    Check if any data is available for the provided date (year, month and day)
    '''
    args = request.args
    year = args.get("year")
    month = args.get("month").zfill(2)
    day = args.get("day").zfill(2)
    sat_points_path = Path(f"./output/{year}/{month}/{day}/sat_points")
    sat_track_path = Path(f"./output/{year}/{month}/{day}/sat_track")
    stations_path = Path(f"./output/{year}/{month}/{day}/stations")

    satellite = args.get("sat")
    if not satellite:
        sat_points_bool,sat_track_bool,stations_bool = False,False,False
        if sat_points_path.exists() and sat_points_path.stat().st_size>64:
            sat_points_bool = True
        if sat_track_path.exists() and sat_track_path.stat().st_size>64:
            sat_track_bool = True
        if stations_path.exists() and stations_path.stat().st_size>64:
            stations_bool = True
        result = {
            "sat_points":sat_points_bool,
            "sat_track":sat_track_bool,
            "stations":stations_bool
        }
        return jsonify(result)
    else:
        sat_points_path = sat_points_path / (satellite+".json")
        sat_track_path = sat_track_path / (satellite+".json")
        sat_points_bool,sat_track_bool,stations_bool = False,False,False
        if sat_points_path.exists() and sat_points_path.stat().st_size>0:
            sat_points_bool = True
        if sat_track_path.exists() and sat_track_path.stat().st_size>0:
            sat_track_bool = True
        if stations_path.exists() and stations_path.stat().st_size>0:
            stations_bool = True
        result = {
            "sat_points":sat_points_bool,
            "sat_track":sat_track_bool,
            "stations":stations_bool
        }
        return jsonify(result)

@app.route('/sendmail',methods=["POST"])
def send_email():
    mail_json = request.get_json(force=True)
    fullName = mail_json['fullName']
    fromMail = mail_json['email']
    msg = mail_json['message']
    send_mail(fromMail,fullName,msg)
    return jsonify({"message":"ok!"})

@app.route('/data/<string:data_id>/<string:prn>',methods=["GET"])
def get_data(data_id,prn):
    '''
    Options for data_id are: 
        igs_stations
        sat_points
        timeseries
        sat_track
    '''
    args = request.args
    year = args.get("year")
    month = args.get("month").zfill(2)
    day = args.get("day").zfill(2)

    if data_id=="igs_stations":
        filepath = Path(f"./output/{year}/{month}/{day}/stations/stations.json")
    else:
        filepath = Path(f"./output/{year}/{month}/{day}/{data_id}/{prn}.json")

    if not filepath.exists():
        abort(404,"That's an error. We didn't find the data you are looking for.")

    with filepath.open("r") as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/apod/<string:data>',methods=["GET"])
def get_APOD(data):
    if data=="dates":
        return jsonify(Nasa.get_APOD_dates())

    args = request.args
    year = args.get("year")
    month = args.get("month").zfill(2)
    day = args.get("day").zfill(2)
    closest = args.get("closest") == "true"

    prev_date = datetime(year=int(year),month=int(month),day=int(day))
    result = get_apod(year,month,day,data)
    if closest:
        while not result:
            new_date = prev_date - timedelta(days=1)
            new_date_strs = datetime.strftime(new_date,"%Y/%m/%d").split('/')
            result = get_apod(new_date_strs[0],new_date_strs[1],new_date_strs[2],data)
            prev_date = new_date

    if not result:
        abort(404,"That's an error. We didn't find the data you are looking for.")

    if data=="json":
        return jsonify(result)
    elif data=="image":
        return send_file(result)

@app.route('/audiosample',methods=["POST"])
def classify_audio_sample():
    time1 = time.time()
    webm_file = get_temp_file("webm")
    wav_file = get_temp_file("wav")

    time2 = time.time()
    print(f"Getting temp files took {time2-time1} seconds")
    with webm_file.open("bx") as f:
        f.write(request.data)
    time3 = time.time()
    print(f"Writing webm file took {time3-time2} seconds")

    subprocess.run(
        ["ffmpeg","-i",str(webm_file),"-vn",str(wav_file)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)

    time4 = time.time()
    print(f"FFMPEG took {time4-time3} seconds")

    result = app.mclas.predict(wav_file,verbose=True)
    time5 = time.time()
    print(f"Prediction took {time5-time4} seconds")

    '''
    if webm_file.exists():
        webm_file.unlink()
    if wav_file.exists():
        wav_file.unlink()
    '''

    if not result:
        abort(404,"We couldn't make a prediction with the provided audio sample...")

    time6 = time.time()
    print(f"Unlinking took {time6-time5} seconds")
    print(f"Total execution took {time6-time1} seconds")

    return jsonify(result)


if __name__=="__main__":
    app.run()
