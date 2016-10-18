"""
Created on Oct 15, 2016

@author: yangr
"""
import pandas as pd

from database import crud


def select_record(records_id):
    query = "SELECT GyroPoints.roll, GyroPoints.pitch, GyroPoints.yaw, AccessPoints.surge, AccessPoints.sway, AccessPoints.heave " \
            "FROM GyroPoints INNER JOIN AccessPoints " \
            "ON GyroPoints.record_id = %s " \
            "AND GyroPoints.timestamp = AccessPoints.timestamp " \
            "ORDER BY GyroPoints.timestamp ASC"
    args = [records_id]
    return crud.read_all(query, args)


def download_record(record_id):
    df = pd.DataFrame(select_record(record_id))
    return df.to_csv()
