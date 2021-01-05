import flask
import json
import pandas as pd
from pathlib import Path
from flask import jsonify,request,abort
from flask_cors import CORS

from data_download import Celestrak,IGS
from conversions import norad2prn

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

cors = CORS(app,resources={
    "r/*":{
        "origins":"333b001b0394.ngrok.io"
    }
})

@app.route('/prns',methods=["GET"])
def get_prns():
    prns = Celestrak.get_prns()
    return jsonify(prns)

@app.route('/stations',methods=["GET"])
def get_stations():
    result = IGS.get_IGS_station_list()
    return jsonify(result)

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

    print(filepath)
    if not filepath.exists():
        abort(404,"That's an error. We didn't find the data you are looking for.")

    with filepath.open("r") as f:
        data = json.load(f)
    return jsonify(data)
 
    

if __name__=="__main__":
    app.run()