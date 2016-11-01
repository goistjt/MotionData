from flask_master.flask_server import app

if __name__ == '__main__':
    # todo: adjust which *_config.ini file is being used in python_mysql_dbconfig.py
    # app.run(host='0.0.0.0', port=80, debug=True)  # Use this for production
    app.run()  # This is for local execution