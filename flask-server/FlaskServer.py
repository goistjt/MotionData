import _mysql
from flask import Flask, jsonify, request
import requests


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


app = Flask(__name__)
# db = _mysql.connect(user='root',
#                     passwd='csse',
#                     host='six-dof.csse.rose-hulman.edu',
#                     port=3306,
#                     db='six-dof')


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
    # db.query("""SELECT * FROM GyroPoints LIMIT 1""")
    # result = db.use_result()
    # result = result.fetch_row()
    # return jsonify(row=str(result))
    r = requests.get('http://www.google.com')
    return r.status_code


# used to check for sql injection later on
# def is_possible_injection(attack_vector):
#     if bool(re.search('[;,\'\"\\/()]', attack_vector)):
#         raise InvalidUsage(
#             "Invalid characters contained in query parameters",
#             status_code=666)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80, debug=True)  # Use this for production
    app.run()  # This is for local execution
