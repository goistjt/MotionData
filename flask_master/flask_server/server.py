import base64
import zlib
import json

from flask import jsonify, request, render_template
import re
from pathlib import Path
import datetime
import pandas as pd

import sys
import string
import os
import shutil
import subprocess
import platform

from data_analysis import data_analysis as da
from flask_server import app, crud, data_lock, upload_files


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_missing_argument(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def index():
    sessions = crud.get_all_sessions()
    return render_template("index.html", table=get_html(sessions), android_route=get_android_route())


def get_html(sessions):
    html = ""
    for s in sessions:
        date = datetime.datetime.fromtimestamp(s[2] / 1e3)
        desc = s[1]
        sess_id = s[0]
        records = crud.get_all_records_from_session(sess_id)
        recs = ""
        for r in records:
            rid = r[0]
            curr = """<tr style="display: table-row;">\n
                       <td>{}</td>\n
                       <td>\n
                           <input id="raw_button" type="submit" name="rr_{}"
                               onclick="clicked_raw('{}', 'r')" value="Download Raw Data" />\n
                           <input id="analyzed_button" type="submit" name="ar_{}"
                               onclick="clicked_analyzed('{}', 'r')" value="Download Analyzed Data" />\n
                       </td>\n
                   </tr>\n""".format(rid, rid, rid, rid, rid)
            recs += curr

        sess = """
                   <tr class="master">\n
                   <td>{}</td>\n
                   <td>{}</td>\n
                   <td>{}</td>\n
                   <td>\n
                       <input id="raw_button" type="submit" name="ras_{}"
                       onclick="clicked_raw('{}', 's')" value="Download Raw Averaged Session" />\n
                       <input id="analyzed_button" type="submit" name="as_{}"
                       onclick="clicked_analyzed('{}', 's')" value="Download Analyzed Session" />\n
                       <input type="file" id="ufs_{}" />
                       <input id="upload_button" type="submit" name="us_{}"
                       onclick="clicked_upload('{}', 's')" value="Upload Record" />\n
                   </td>\n
                   <td><div class="arrow"></div></td>\n
               </tr>\n
               <tr style="display: none;">\n
                   <td colspan="6">\n
                       <table id="records" class="table table-bordered table-hover table-striped">\n
                           <thead>\n
                               <tr>\n
                                   <th>Record ID</th>\n
                                   <th>Download</th>\n
                               </tr>\n
                           </thead>\n
                           <tbody>\n
                               {}
                           </tbody>\n
                       </table>\n
                   </td>\n
               </tr>\n""".format(sess_id, desc, date, sess_id, sess_id, sess_id, sess_id, sess_id, sess_id, sess_id,
                                 recs)
        html += sess
    return html


@app.route("/tables.html")
def tables():
    return render_template("tables.html")


@app.route("/getRecordRaw/<record_id>")
def get_record_data_raw(record_id=[]):
    txt = da.download_record_raw(record_id)
    filename = "record_raw_{}_{}.txt".format(record_id, str(datetime.datetime.now()))
    response = {'Content-Disposition': 'attachment;',
                'filename': filename,
                'mimetype': 'text/csv',
                'data': txt}
    return jsonify(response)


@app.route("/getRecordAnalyzed/<record_id>")
def get_record_data_analyzed(record_id=[]):
    txt = da.download_record_analyzed(record_id)
    filename = "record_analyzed_{}_{}.txt".format(record_id, str(datetime.datetime.now()))
    response = {'Content-Disposition': 'attachment;',
                'filename': filename,
                'mimetype': 'text/csv',
                'data': txt}
    return jsonify(response)


@app.route("/getSessionRaw/<session_id>")
def get_session_data_raw(session_id=[]):
    txt = da.download_session_raw(session_id)
    filename = "session_raw_{}_{}.txt".format(session_id, str(datetime.datetime.now()))
    response = {'Content-Disposition': 'attachment;',
                'filename': filename,
                'mimetype': 'text/csv',
                'data': txt}
    return jsonify(response)


@app.route("/getSessionAnalyzed/<session_id>")
def get_session_data_analyzed(session_id=[]):
    txt = da.download_session_analyzed(session_id)
    filename = "session_analyzed_{}_{}.txt".format(session_id, str(datetime.datetime.now()))
    response = {'Content-Disposition': 'attachment;',
                'filename': filename,
                'mimetype': 'text/csv',
                'data': txt}
    return jsonify(response)


@app.route("/createSession", methods=["POST"])
def create_session():
    """ {sess_desc: "",
         accelModels: [{time_val: long, x_val: float, y_val: float, z_val: float}],
         gyroModels: [{time_val: long, pitch_val: float, roll_val: float, yaw_val: float}],
         device_id: "",
         device_name: "",
         begin: long} """

    b64 = base64.b64decode(request.data)
    request_data = str(zlib.decompress(b64, 16 + zlib.MAX_WBITS), "utf-8")
    data = json.loads(request_data)

    desc = data['sess_desc']
    accel_data = data['accelModels']
    gyro_data = data['gyroModels']
    device_id = data['device_id']
    device_name = data['device_name']
    start = data['begin']

    if desc is None or accel_data is None or gyro_data is None or device_id is None \
            or device_name is None or start is None:
        raise InvalidUsage(
            "Unable to send request without {}.".format(
                "description" if desc is None else "accel data" if accel_data is None
                else "gyro data" if gyro_data is None else "device ID" if device_id is None
                else "device name" if device_name is None else "start time" if start is None
                else "Error: Nothing was left empty"),
            status_code=701)

    is_possible_injection(desc)

    print("accel points: {}, gyro points: {}".format(len(accel_data), len(gyro_data)))

    sess_id = crud.create_session(desc, start)
    rec_id = crud.create_record(sess_id, device_id)
    device_name_db = crud.get_device_name(device_id)
    if device_name_db is None:
        crud.create_device_entry(device_id, device_name)
    if device_name != device_name_db:
        crud.update_device_entry(device_id, device_name)

    gyro_points = []
    accel_points = []

    here = Path(__file__).parent.parent.resolve()
    accel_file = "{}\\db_upload_files\\accel_{}_{}.csv".format(here, sess_id, rec_id)
    gyro_file = "{}\\db_upload_files\\gyro_{}_{}.csv".format(here, sess_id, rec_id)

    for point in accel_data:
        x = point['x_val']
        y = point['y_val']
        z = point['z_val']
        time = point['time_val']

        # dump points to csv
        accel_points.append((rec_id, time, x, y, z))

    accel = pd.DataFrame(accel_points)
    accel.to_csv(accel_file, index=False)
    # get lock
    with data_lock:
        # add {type, file} to upload_files
        upload_files.append(["accel", accel_file])

    for point in gyro_data:
        roll = point['roll_val']
        pitch = point['pitch_val']
        yaw = point['yaw_val']
        time = point['time_val']
        # dump points to csv
        gyro_points.append((rec_id, time, roll, pitch, yaw))

    gyro = pd.DataFrame(gyro_points)
    gyro.to_csv(gyro_file, index=False)
    # get lock
    with data_lock:
        # add {type, file} to upload_files
        upload_files.append(["gyro", gyro_file])

    return jsonify(session_id=sess_id, record_id=rec_id)


@app.route("/addToSession", methods=["POST"])
def add_to_session():
    """ {accelModels: [{time_val: long, x_val: float, y_val: float, z_val: float}],
         gyroModels: [{time_val: long, pitch_val: float, roll_val: float, yaw_val: float}],
         device_id: "",
         device_name: "",
         sess_id: ""} """
    b64 = base64.b64decode(request.data)
    request_data = str(zlib.decompress(b64, 16 + zlib.MAX_WBITS), "utf-8")
    data = json.loads(request_data)

    sess_id = data['sess_id']
    accel_data = data['accelModels']
    gyro_data = data['gyroModels']
    device_id = data['device_id']
    device_name = data['device_name']

    if sess_id is None or accel_data is None or gyro_data is None \
            or device_name is None or device_id is None:
        raise InvalidUsage(
            "Unable to send request without {}.".format(
                "session id" if sess_id is None else "accel data" if accel_data is None
                else "gyro data" if gyro_data is None else "device ID" if device_id is None
                else "device name" if device_name is None else "Error: Nothing was left empty"),
            status_code=701)

    print("accel points: {}, gyro points: {}".format(len(accel_data), len(gyro_data)))

    rec_id = crud.create_record(sess_id, device_id)
    device_name_db = crud.get_device_name(device_id)
    if device_name_db is None:
        crud.create_device_entry(device_id, device_name)
    if device_name != device_name_db:
        crud.update_device_entry(device_id, device_name)

    gyro_points = []
    accel_points = []

    here = Path(__file__).parent.parent.resolve()
    accel_file = "{}\\db_upload_files\\accel_{}_{}.csv".format(here, sess_id, rec_id)
    gyro_file = "{}\\db_upload_files\\gyro_{}_{}.csv".format(here, sess_id, rec_id)

    for point in accel_data:
        x = point['x_val']
        y = point['y_val']
        z = point['z_val']
        time = point['time_val']

        # dump points to csv
        accel_points.append((rec_id, time, x, y, z))

    accel = pd.DataFrame(accel_points)
    accel.to_csv(accel_file, index=False)
    # get lock
    with data_lock:
        # add {type, file} to upload_files
        upload_files.append(["accel", accel_file])

    for point in gyro_data:
        roll = point['roll_val']
        pitch = point['pitch_val']
        yaw = point['yaw_val']
        time = point['time_val']
        # dump points to csv
        gyro_points.append((rec_id, time, roll, pitch, yaw))

    gyro = pd.DataFrame(gyro_points)
    gyro.to_csv(gyro_file, index=False)
    # get lock
    with data_lock:
        # add {type, file} to upload_files
        upload_files.append(["gyro", gyro_file])

    return jsonify(session_id=sess_id, record_id=rec_id)


@app.route("/deleteSession", methods=['DELETE'])
def delete_session():
    data = request.get_json(force=True)
    sess_id = data["sess_id"]
    crud.delete_entire_session(sess_id)
    return jsonify(session_id=sess_id)


@app.route("/getSessions/<device_id>")
def get_sessions(device_id):
    result = list(crud.get_sessions(device_id))
    ret_list = []
    for row in result:
        row = list(row)
        row[2] = datetime.datetime.fromtimestamp(row[2] / 1e3)
        ret_list.append(dict(id=row[0], desc=row[1], date=row[2]))
    return jsonify(sessions=ret_list)


"""
Used as default Android cache location resource
"""


def get_android_route():
    return os.path.dirname(os.path.realpath(__file__)) + "/android_files"


"""
Route in charge of updating Android cache locally - returns 503 if phone unplugged, 200 if phone transfer successful
Has to check for OS in order to get location "correct" - still RELIES ON SPECIFIC INSTALL LOCATION - 500 if not
expected OS
"""


@app.route("/updateAndroidCache")
def update_android_files():

    system_name = platform.system()

    if system_name == 'Windows':
        adb_location = 'C:/Android/sdk/platform-tools/adb'

    elif system_name == 'Linux':
        adb_location = "/usr/bin/adb"

    else:
        return jsonify(status_code=500)

    repository_dir_location = get_android_route()

    app_repo_location = 'sdcard/Android/data/edu.rose_hulman.nswccrane.dataacquisition/files/records'

    if not os.path.exists(get_android_route()):
        os.makedirs(get_android_route())

    cmd = 'pull'

    sep = ' '

    cmd = adb_location + sep + cmd + sep + app_repo_location + sep + repository_dir_location

    try:
        subprocess.check_output(cmd.split())

    except:
        # TODO: This is an area where additional status codes could and probably should be used
        e = sys.exc_info()[0]
        print(e)
        return jsonify(status_code=503)

    return jsonify(status_code=200)


"""
Route in charge of deleting / clearing the Android cache.
"""


@app.route("/clearAndroidCache")
def delete_android_cache():
    if os.path.exists(get_android_route()):
        try:
            shutil.rmtree(get_android_route())

        except OSError as e:
            print(e)
            return jsonify(status_code=500)

    return jsonify(status_code=200)

# used to check for sql injection
def is_possible_injection(attack_vector):
    if bool(re.search('[;\"\\/()]', attack_vector)):
        raise InvalidUsage(
            "Invalid characters contained in query parameters",
            status_code=666)
