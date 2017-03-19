from flask import Flask
import threading
import atexit
import os
from pathlib import Path
from flask_compress import Compress
import shutil

from database import crud_class

POOL_TIME = 15  # Seconds

upload_files = []
data_lock = threading.Lock()
t = threading.Thread()
local = False
crud = None
compress = Compress()


def create_app():
    app = Flask(__name__)
    compress.init_app(app)
    global crud
    crud = crud_class.Crud()

    def interrupt():
        global t
        global crud
        t.join()
        t.cancel()
        crud.close()

    def upload_to_db():
        global upload_files
        global t
        data = []
        with data_lock:
            # check if there are any files to upload
            if len(upload_files) > 0:
                # get the file to upload
                data = upload_files.pop(0)

        if data:
            # get file type & name
            data_type = data[0]
            file = data[1]
            file = file.replace("\\", "\\\\")

            # check type
            if data_type == "accel":
                crud.bulk_insert_accel_points(file, local)
            else:
                crud.bulk_insert_gyro_points(file, local)

            os.remove(file.replace("\\\\", "\\"))

        t = threading.Timer(POOL_TIME, upload_to_db, ())
        t.start()

    def upload_start():
        global t
        global upload_files

        here = Path(__file__).parent.parent.resolve()
        files = []
        for (path, dirnames, filenames) in os.walk('../flask_master\\db_upload_files'):
            files.extend("{}\\db_upload_files\\{}".format(here, name) for name in filenames)
        for f in files:
            if 'accel' in f:
                file_type = 'accel'
            else:
                file_type = 'gyro'
            upload_files.append([file_type, f])

        t = threading.Timer(POOL_TIME, upload_to_db, ())
        t.start()

    upload_start()
    atexit.register(interrupt)
    return app

if os.environ.get('TRAVIS') is None:
    app = create_app()
else:
    app = Flask(__name__)

import flask_server.server


def delete_android_cache():
    if os.path.exists(server.get_android_route()):
        shutil.rmtree(server.get_android_route())

import atexit
atexit.register(delete_android_cache)
