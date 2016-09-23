from flask import Flask, jsonify, request
from ServerException import *

app = Flask(__name__)


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


# used to check for sql injection later on
# def is_possible_injection(attack_vector):
#     if bool(re.search('[;,\'\"\\/()]', attack_vector)):
#         raise InvalidUsage(
#             "Invalid characters contained in query parameters",
#             status_code=666)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80, debug=True)  # Use this for production
    app.run()  # This is for local execution
