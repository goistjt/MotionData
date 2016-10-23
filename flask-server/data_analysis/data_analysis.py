"""
Created on Oct 15, 2016

@author: yangr
"""
import pandas as pd

from database import crud

COLLECT_TIME = 0.040

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

def get_excursions_for_dataset(rows):
    raw_exc = []
    prev_exc = 0
    prev_vel = 0
    prev_accel = 0
    for row in rows:
        new_accel = row[0]
        new_vel = determine_next_velocity(prev_vel, prev_accel, new_accel)
        new_exc = determine_next_excursion(prev_exc, prev_vel, prev_accel, new_accel)
        raw_exc.append(new_exc)
        prev_exc = new_exc
        prev_vel = new_vel
        prev_accel = new_accel
    return raw_exc

def determine_next_excursion(prev_exc, prev_vel, prev_accel, new_accel):
    return prev_exc + prev_vel * COLLECT_TIME + (1/2) * prev_accel * (COLLECT_TIME ** 2) + (1/6) * (new_accel - prev_accel) * (COLLECT_TIME ** 2)

def determine_next_velocity(prev_vel, prev_accel, new_accel):
    return prev_vel + prev_accel * COLLECT_TIME + (1/2) * (new_accel - prev_accel) * (COLLECT_TIME ** 2)
