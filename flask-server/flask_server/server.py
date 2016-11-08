from flask import jsonify, request, render_template, Response
import re
import datetime

from data_analysis import data_analysis as da
from database import crud_class
from flask_server import app


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


# /echo?usernames=<insert here>
@app.route('/echo')
def echo():
    users = request.args.get('usernames').split(',')
    return jsonify(usernames=users)


@app.route('/hello-world')
def hello_world():
    return 'Hello World!'


@app.route('/gyro')
def gyro():
    crud = crud_class.Crud()
    result = crud.read_one("""SELECT * FROM GyroPoints LIMIT 1""")
    crud.close()
    return jsonify(row=str(result))


@app.route('/session')
def session():
    crud = crud_class.Crud()
    result = crud.read_all("SELECT * FROM Session")
    crud.close()
    return jsonify(row=str(result))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tables.html")
def tables():
    return render_template("tables.html")


@app.route("/getRecord/<record_id>")
def get_record_data(record_id=[]):
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    txt = da.download_record(record_id)
    return Response(
        txt,
        mimetype="text",
        headers={"Content-disposition":
                     "attachment; filename=record.txt"})


@app.route("/createSession", methods=["POST"])
def create_session():
    """ {sess_desc: "",
         accelModels: [{time_val: long, x_val: float, y_val: float, z_val: float}],
         gyroModels: [{time_val: long, pitch_val: float, roll_val: float, yaw_val: float}],
         device_id: "",
         begin: long} """
    data = request.get_json(force=True)
    desc = data['sess_desc']
    accel_data = data['accelModels']
    gyro_data = data['gyroModels']
    device_id = data['device_id']
    start = data['begin']

    if desc is None or accel_data is None or gyro_data is None or device_id is None or start is None:
        raise InvalidUsage(
            "Unable to send request without {}.".format(
                "description" if desc is None else "accel data" if accel_data is None
                else "gyro data" if gyro_data is None else "device ID" if device_id is None
                else "start time" if start is None else "Error: Nothing was left empty"),
            status_code=701)

    is_possible_injection(desc)

    print("accel points: {}, gyro points: {}".format(len(accel_data), len(gyro_data)))

    crud = crud_class.Crud()
    sess_id = crud.create_session(desc, start)
    rec_id = crud.create_record(sess_id, device_id)
    for point in accel_data:
        x = point['x_val']
        y = point['y_val']
        z = point['z_val']
        time = point['time_val']
        crud.insert_accel_points(rec_id, time, x, y, z)

    for point in gyro_data:
        roll = point['roll_val']
        pitch = point['pitch_val']
        yaw = point['yaw_val']
        time = point['time_val']
        crud.insert_gyro_points(rec_id, time, roll, pitch, yaw)

    crud.close()
    return jsonify(session_id=sess_id, record_id=rec_id)


@app.route("/addToSession", methods=["POST"])
def add_to_session():
    """ {accelModels: [{time_val: long, x_val: float, y_val: float, z_val: float}],
         gyroModels: [{time_val: long, pitch_val: float, roll_val: float, yaw_val: float}],
         device_id: "",
         sess_id: ""} """
    data = request.get_json(force=True)
    sess_id = data['sess_id']
    accel_data = data['accelModels']
    gyro_data = data['gyroModels']
    device_id = data['device_id']

    if sess_id is None or accel_data is None or gyro_data is None or device_id is None:
        raise InvalidUsage(
            "Unable to send request without {}.".format(
                "session id" if sess_id is None else "accel data" if accel_data is None
                else "gyro data" if gyro_data is None else "device ID" if device_id is None
                else "Error: Nothing was left empty"),
            status_code=701)

    print("accel points: {}, gyro points: {}".format(len(accel_data), len(gyro_data)))

    crud = crud_class.Crud()
    rec_id = crud.create_record(sess_id, device_id)
    for point in accel_data:
        x = point['x_val']
        y = point['y_val']
        z = point['z_val']
        time = point['time_val']
        crud.insert_accel_points(rec_id, time, x, y, z)

    for point in gyro_data:
        roll = point['roll_val']
        pitch = point['pitch_val']
        yaw = point['yaw_val']
        time = point['time_val']
        crud.insert_gyro_points(rec_id, time, roll, pitch, yaw)

    crud.close()
    return jsonify(session_id=sess_id, record_id=rec_id)


@app.route("/deleteSession", methods=['DELETE'])
def delete_session():
    data = request.get_json(force=True)
    sess_id = data["sess_id"]

    crud = crud_class.Crud()
    crud.delete_entire_session(sess_id)
    crud.close()
    return jsonify(session_id=sess_id)


@app.route("/getSessions/<device_id>")
def get_sessions(device_id):
    crud = crud_class.Crud()
    result = list(crud.get_sessions(device_id))
    ret_list = []
    for row in result:
        row = list(row)
        row[2] = datetime.datetime.fromtimestamp(row[2] / 1e3)
        ret_list.append(dict(id=row[0], desc=row[1], date=row[2]))
    crud.close()
    return jsonify(sessions=ret_list)


# used to check for sql injection
def is_possible_injection(attack_vector):
    if bool(re.search('[;\"\\/()]', attack_vector)):
        raise InvalidUsage(
            "Invalid characters contained in query parameters",
            status_code=666)
