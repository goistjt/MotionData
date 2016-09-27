from flask import Flask, jsonify, request
from ServerException import *
import _mysql

app = Flask(__name__)
db = _mysql.connect(user='root',
                    passwd='csse',
                    host='six-dof.csse.rose-hulman.edu',
                    port=3306,
                    db='six-dof')


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
    db.query("""SELECT * FROM GyroPoints LIMIT 1""")
    result = db.use_result()
    result = result.fetch_row()
    return jsonify(row=str(result))


# used to check for sql injection later on
# def is_possible_injection(attack_vector):
#     if bool(re.search('[;,\'\"\\/()]', attack_vector)):
#         raise InvalidUsage(
#             "Invalid characters contained in query parameters",
#             status_code=666)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80, debug=True)  # Use this for production
    app.run()  # This is for local execution
