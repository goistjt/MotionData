import base64
import zlib
import json

from flask import jsonify, request, render_template
import re
from pathlib import Path
import datetime
import pandas as pd
import math

import os
import shutil
import subprocess
import platform

from data_analysis import data_analysis as da
from flask_server import app, crud, data_lock, upload_files


class InvalidUsage(Exception):
    """
        This class is used in handling errors due to invalid usage of the server
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """
            Sets up the error fields
        :param message: the error message given
        :param status_code: the error status code
        :param payload: the error contents
        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """
        :return: A dictionary of the error contents and message
        """
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_missing_argument(error):
    """
        Handles a 'missing argument' error
    :param error: The error thrown
    :return: An error response to be shown to the user
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def index():
    """
        Makes a call to generate the sessions table and renders the index page of the website
    :return: renders the index page of the website
    """
    sessions = crud.get_all_sessions()
    if sessions is None:
        table = get_html_no_sessions()
    else:
        table = get_html_sessions(sessions)
    return render_template("index.html", table=table, android_route=get_android_route())


def get_html_no_sessions():
    """
        Creates a table row that contains a message for the user stating that there aren't any
        sessions in the database
    :return: the empty sessions table
    """
    html = """<tr class="master">\n
                   <td colspan="6"><p>No recording sessions in database</p></td>\n
               </tr>\n"""
    return html


def get_html_sessions(sessions):
    """
        Creates a table row for each session with nested table rows for each record
        within that session.
        Each Session row gives the session ID, session description, recording date, and session download buttons
        Each Record row gives the device name (or record ID if no device name is set) and the record download buttons
    :return: the full sessions table
    """
    html = ""
    for s in sessions:
        date = datetime.datetime.fromtimestamp(s[2] / 1e3)
        desc = s[1]
        sess_id = s[0]
        records = crud.get_all_records_from_session(sess_id)
        recs = ""
        for r in records:
            rid = r[0]
            dev_id = r[2]
            dev_name = crud.get_device_name(dev_id)
            if dev_name == () or dev_name[0] == '':
                dev_name = dev_id
            else:
                dev_name = dev_name[0]
            curr = """<tr style="display: table-row;">\n
                       <td>{}</td>\n
                       <td>\n
                           <input id="raw_button" type="submit" name="rr_{}"
                               onclick="clicked_raw('{}', 'r', '{}')" value="Download Raw Data" />\n
                           <input id="analyzed_button" type="submit" name="ar_{}"
                               onclick="clicked_analyzed('{}', 'r', '{}')" value="Download Analyzed Data" />\n
                       </td>\n
                   </tr>\n""".format(dev_name, rid, rid, dev_name, rid, rid, dev_name)
            recs += curr

        sess = """<tr class="master">\n
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
                   <td id="record_table" colspan="6">\n
                       <table id="records" class="table table-bordered table-hover">\n
                            <thead>\n
                               <tr>\n
                                   <th>Device Name / ID</th>\n
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
    """
        Renders the website page that contains a table of the server endpoints and their usage
    :return: Renders the tables page
    """
    return render_template("tables.html")


@app.route("/getRecordRaw/<record_id>")
def get_record_data_raw(record_id):
    """
        Gets the record data from the database and downloads it to a .txt file in
        the required format
    :param record_id: the record ID that we are downloading data from
    :return: The raw record data
    """
    txt = da.download_record_raw(record_id)
    filename = "record_raw_()_{}.txt".format(str(datetime.datetime.now()))
    response = {'Content-Disposition': 'attachment;',
                'filename': filename,
                'mimetype': 'text/csv',
                'data': txt}
    return jsonify(response)


@app.route("/getRecordAnalyzed/<record_id>")
def get_record_data_analyzed(record_id):
    """
        Gets the record data from the database, analyzes it, and downloads it to a .txt file in
        the required format
    :param record_id: the record ID that we are downloading data from
    :return: The analyzed record data
    """
    txt = da.download_record_analyzed(record_id)
    filename = "record_analyzed_()_{}.txt".format(str(datetime.datetime.now()))
    response = {'Content-Disposition': 'attachment;',
                'filename': filename,
                'mimetype': 'text/csv',
                'data': txt}
    return jsonify(response)


@app.route("/getSessionRaw/<session_id>")
def get_session_data_raw(session_id):
    """
        Gets the record data from the database for each record in the indicated session,
        does a basic timestamp match up, and downloads it to a .txt file in the required format
    :param session_id: the session ID that we are downloading data for
    :return: The raw session data
    """
    txt = da.download_session_raw(session_id)
    filename = "session_raw_{}_{}.txt".format(session_id, str(datetime.datetime.now()))
    response = {'Content-Disposition': 'attachment;',
                'filename': filename,
                'mimetype': 'text/csv',
                'data': txt}
    return jsonify(response)


@app.route("/getSessionAnalyzed/<session_id>")
def get_session_data_analyzed(session_id):
    """
        Gets the record data from the database for each record in the indicated session,
        does a basic timestamp match up, performs the data analysis, and downloads it to
        a .txt file in the required format
    :param session_id: the session ID that we are downloading data for
    :return: The raw session data
    """
    txt = da.download_session_analyzed(session_id)
    filename = "session_analyzed_{}_{}.txt".format(session_id, str(datetime.datetime.now()))
    response = {'Content-Disposition': 'attachment;',
                'filename': filename,
                'mimetype': 'text/csv',
                'data': txt}
    return jsonify(response)


def decode_to_json(data):
    """
        Performs a base64 decode, unzips, and dumps the input
        data into JSON format
    :param data: The data to decode and convert ot JSON
    :return: The JSON data
    """
    b64 = base64.b64decode(data)
    request_data = str(zlib.decompress(b64, 16+zlib.MAX_WBITS), "utf-8")
    json_data = json.loads(request_data)
    return json_data


def update_device_name_db(device_name, device_id):
    """
        Gets the database device name for the provided device ID
        Checks if the provided device name and database device name
            match, and updates the database entry if they don't
    :param device_name: The most recent name for the device
    :param device_id: The device ID
    """
    device_name_db = crud.get_device_name(device_id)
    if device_name_db == ():
        crud.create_device_entry(device_id, device_name)
    if device_name != device_name_db:
        crud.update_device_entry(device_id, device_name)


def create_data_file(sess_id, rec_id, data, data_type):
    """
        Creates a .csv file, converts the data from JSON to an array, adds the array of data
        to the .csv file, adds the file to the queue to be uploaded by the background
        thread
    :param sess_id: The session ID the data is a part of
    :param rec_id: The record ID the data is related to
    :param data: The accelerometer or gyroscope data that is being added ot the file
    :param data_type: The data type that the file is being create for; either 'accel' or 'gyro'
    """
    here = Path(__file__).parent.parent.resolve()

    directory = "{}/db_upload_files/".format(here)

    if not os.path.exists(directory):
        os.makedirs(directory)

    file = directory + "{}_{}_{}.csv".format(data_type, sess_id, rec_id)

    points = []
    for point in data:
        # todo: if 'gyro' convert to degrees from radians
        time = point['time_val']
        if data_type == "accel":
            one = point['x_val']
            two = point['y_val']
            three = point['z_val']
        else:
            one = math.degrees(point['roll_val'])
            two = math.degrees(point['pitch_val'])
            three = math.degrees(point['yaw_val'])

        # dump points to csv
        points.append((rec_id, time, one, two, three))

    data = pd.DataFrame(points)
    data.to_csv(file, index=False)
    # get lock
    with data_lock:
        # add {type, file} to upload_files
        upload_files.append([data_type, file])


@app.route("/createSession", methods=["POST"])
def create_session():
    """
        Creates a new session and record in the database with the data from the POST body
    :post format:
        {sess_desc: "",
         accelModels: [{time_val: long, x_val: float, y_val: float, z_val: float}],
         gyroModels: [{time_val: long, pitch_val: float, roll_val: float, yaw_val: float}],
         device_id: "",
         device_name: "",
         begin: long}
    :return: The new session and record IDs
    """

    data = decode_to_json(request.data)

    desc = data['sess_desc']
    accel_data = data['accelModels']
    gyro_data = data['gyroModels']
    device_id = data['device_id']
    device_name = data['device_name']
    start = data['begin']

    return create_session_from_data(desc, accel_data, gyro_data, device_id, device_name, start)


@app.route("/createSessionFromLocal", methods=["POST"])
def create_session_from_local():
    """
    Creates a new session and record in the database with the data from the POST body. This is meant to be the
    specific enpoint for accomplishing this task from a local source in case there is a clear distinction between
    the tasks of local / nonlocal. Uses the "content" form to get the post data.

        :post format:
        {sess_desc: "",
         accelModels: [{time_val: long, x_val: float, y_val: float, z_val: float}],
         gyroModels: [{time_val: long, pitch_val: float, roll_val: float, yaw_val: float}],
         device_id: "",
         device_name: "",
         begin: long}

    :return: The new session and record IDs
    """

    data = decode_to_json(request.form['content'])

    desc = data['sess_desc']
    accel_data = data['accelModels']
    gyro_data = data['gyroModels']
    device_id = data['device_id']
    device_name = data['device_name']
    start = data['begin']

    return create_session_from_data(desc, accel_data, gyro_data, device_id, device_name, start)


def create_session_from_data(desc, accel_data, gyro_data, device_id, device_name, start):

    """
    Extracted out from the endpoints that use it, this function is meant to take the data necessary for inserting into
    the session table and perform that action on the database, returning a jsonified result of the action or error.

    :param: desc - description of the session
    :param: accel_data - the acceleration data points to create the session with
    :param: gyro_data - the gyroscopic data points to create the session with
    :param: device_id - the device id associated with this first record for the created session
    :param: device_name - the device name associated with the first record
    :param: start - the start time for the session

    :returns: jsonified result fo the insertion of the session table - includes session id and record id associated
    """
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
    is_possible_injection(device_name)

    update_device_name_db(device_name, device_id)
    sess_id = crud.create_session(desc, start)
    rec_id = crud.create_record(sess_id, device_id)

    create_data_file(sess_id, rec_id, accel_data, "accel")
    create_data_file(sess_id, rec_id, gyro_data, "gyro")

    return jsonify(session_id=sess_id, record_id=rec_id, status_code=200)


@app.route("/addToSession", methods=["POST"])
def add_to_session():
    """
        Creates a new record in the database related to the indicated session using the data from the POST body

        :post format:
        {accelModels: [{time_val: long, x_val: float, y_val: float, z_val: float}],
        gyroModels: [{time_val: long, pitch_val: float, roll_val: float, yaw_val: float}],
        device_id: "",
        device_name: "",
        sess_id: ""}

        :returns: jsonified session id and record id
    """

    data = decode_to_json(request.data)

    sess_id = data['sess_id']
    accel_data = data['accelModels']
    gyro_data = data['gyroModels']
    device_id = data['device_id']
    device_name = data['device_name']

    return add_to_session_from_data(sess_id, accel_data, gyro_data, device_id, device_name)


@app.route("/addToSessionFromLocal", methods=["POST"])
def add_to_session_from_local():
    """
        Creates a new record in the database related to the indicated session using the data from the POST body - this
        is done from local file input in the "content" form

        [{accelModels: [{time_val: long, x_val: float, y_val: float, z_val: float}],
         gyroModels: [{time_val: long, pitch_val: float, roll_val: float, yaw_val: float}],
         device_id: "",
         device_name: "",
         sess_id: ""},
         session_id: ""]

        :returns: jsonified session id and record id
    """

    data = decode_to_json(request.form['content'])

    sess_id = int(request.form['sess_id'])
    accel_data = data['accelModels']
    gyro_data = data['gyroModels']
    device_id = data['device_id']
    device_name = data['device_name']

    return add_to_session_from_data(sess_id, accel_data, gyro_data, device_id, device_name)


def add_to_session_from_data(sess_id, accel_data, gyro_data, device_id, device_name):

    """
        Extracted logic to insert record data into the appropriate tables associated with the given session_id.

        :param: sess_id - the session id to be assocated to
        :param: accel_data - the accelerometer points collected
        :param: gyro_data - the gyroscopic points collected
        :param: device_id - the id of the device the points were collected on
        :param: device_name - the name of the device the points were collected on

        :returns: jsonified session id and record id and status code
    """

    if sess_id is None or accel_data is None or gyro_data is None \
            or device_name is None or device_id is None:
        raise InvalidUsage(
            "Unable to send request without {}.".format(
                "session id" if sess_id is None else "accel data" if accel_data is None
                else "gyro data" if gyro_data is None else "device ID" if device_id is None
                else "device name" if device_name is None else "Error: Nothing was left empty"),
            status_code=701)

    is_possible_injection(device_name)

    update_device_name_db(device_name, device_id)
    rec_id = crud.create_record(sess_id, device_id)

    create_data_file(sess_id, rec_id, accel_data, "accel")
    create_data_file(sess_id, rec_id, gyro_data, "gyro")

    return jsonify(session_id=sess_id, record_id=rec_id, status_code=200)


@app.route("/deleteSession", methods=['DELETE'])
def delete_session():
    """
        Deletes all data related to the session in the database that has the
        session ID provided in the JSON body

        :JSON format:
        {sess_id: ""}

    :return: The session ID
    """
    data = request.get_json(force=True)
    sess_id = data["sess_id"]
    crud.delete_entire_session(sess_id)
    return jsonify(session_id=sess_id)


@app.route("/getSessions/<device_id>")
def get_sessions(device_id):
    """
        Collects a list of all sessions that the current device is not a part of

    :param device_id: the device ID to check against
    :return: List of all unrelated sessions
    """
    result = list(crud.get_sessions_not_related_to_device(device_id))
    ret_list = []
    for row in result:
        row = list(row)
        row[2] = datetime.datetime.fromtimestamp(row[2] / 1e3)
        ret_list.append(dict(id=row[0], desc=row[1], date=row[2]))
    return jsonify(sessions=ret_list)


def get_android_route():
    """
    Used as default Android cache location resource.

    :returns: gives the specified path to the android cache
    """
    return os.path.dirname(os.path.realpath(__file__)) + "/android_files"


@app.route("/updateAndroidCache")
def update_android_files():
    """
    Route in charge of updating Android cache locally - returns 503 if phone unplugged, 200 if phone transfer successful
    Has to check for OS in order to get location "correct" - still RELIES ON SPECIFIC INSTALL LOCATION - 500 if not
    expected OS.

    :returns: jsonified status based on the success of updating the cache
    """
    system_name = platform.system()

    if system_name == 'Windows':
        adb_location = 'C:\\Android\\sdk\\platform-tools\\adb'

    elif system_name == 'Linux':
        adb_location = "/usr/bin/adb"

    else:
        return jsonify(status_code=505)

    repository_dir_location = get_android_route()

    app_repo_location = 'sdcard/Android/data/edu.rose_hulman.nswccrane.dataacquisition/files/records'

    if not os.path.exists(get_android_route()):
        os.makedirs(get_android_route())

    cmd = 'pull'

    space = ' '

    cmd = adb_location + space + cmd + space + app_repo_location + space + repository_dir_location

    try:
        subprocess.check_output(cmd.split())

    except subprocess.CalledProcessError as e:
        print(e)
        return jsonify(status_code=503)

    return jsonify(status_code=200)


@app.route("/clearAndroidCache")
def delete_android_cache():
    """
    Route in charge of deleting / clearing the Android cache.

    :returns: jsonified status code of the success of clearing the cache
    """
    if os.path.exists(get_android_route()):

        try:
            shutil.rmtree(get_android_route())

        except OSError as e:
            print(e)
            return jsonify(status_code=500)

    return jsonify(status_code=200)


def is_possible_injection(attack_vector):
    """
        Checks the input for invalid characters and errors if any are found
        Used to check for SQL injection in the user inputs
    :param attack_vector: the string to check for invalid characters
    :return: Raise InvalidUsage error if an invalid character is found
    """
    if bool(re.search('[;\"\\/()]', attack_vector)):
        raise InvalidUsage(
            "Invalid characters contained in query parameters",
            status_code=666)
