from flask import jsonify, request, render_template, Response

from data_analysis import data_analysis as da
from database import crud
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
# @app.route('/echo')
# def echo():
#     users = request.args.get('usernames').split(',')
#     return jsonify(usernames=users)


@app.route('/hello-world')
def hello_world():
    return 'Hello World!'


@app.route('/gyro')
def gyro():
    result = crud.read_one("""SELECT * FROM GyroPoints LIMIT 1""")
    return jsonify(row=str(result))


@app.route('/session')
def session():
    result = crud.read_all("SELECT * FROM Session")
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


# used to check for sql injection later on
# def is_possible_injection(attack_vector):
#     if bool(re.search('[;,\'\"\\/()]', attack_vector)):
#         raise InvalidUsage(
#             "Invalid characters contained in query parameters",
#             status_code=666)

