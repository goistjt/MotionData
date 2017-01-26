import flask_server

if __name__ == '__main__':
    # note: adjust which *_config.ini file is being used in python_mysql_dbconfig.py
    flask_server.local = True
    # flask_server.app.run(host='0.0.0.0', port=80, debug=True)  # Use this for production

    # flask_server.local = True
    flask_server.app.run()  # This is for local execution
