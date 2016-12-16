from flask_server import app

if __name__ == '__main__':
    # todo: adjust which *_config.ini file is being used in python_mysql_dbconfig.py
    app.run(host='127.0.0.1', port=5000, debug=False)  # Use this for production
    # app.run()  # This is for local execution
