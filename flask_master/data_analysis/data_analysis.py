"""
Created on Oct 15, 2016

@author: yangr
"""
import pandas as pd
import numpy as np

from flask_master.database import crud

import flask_master.data_analysis.kinematics_keeper as kk


def select_record(records_id):
    query = "SELECT GyroPoints.roll, GyroPoints.pitch, GyroPoints.yaw, AccelPoints.surge, AccelPoints.sway, AccelPoints.heave " \
            "FROM GyroPoints INNER JOIN AccelPoints " \
            "ON GyroPoints.record_id = %s " \
            "AND GyroPoints.timestamp = AccelPoints.timestamp " \
            "ORDER BY GyroPoints.timestamp ASC"
    args = [records_id]
    return crud.read_all(query, args)


def download_record(record_id = []):
    df = pd.DataFrame(np.array(select_record(record_id)))
    return df.to_csv(index=False)

def get_excursions(start_time, accel_points, gyro_points):
    raw_excursion_sets = np.array()
    raw_excursion_sets.append([0, 0, 0, 0, 0, 0])
    surge_keeper = kk.KinematicsKeeper(start_time)
    sway_keeper = kk.KinematicsKeeper(start_time)
    heave_keeper = kk.KinematicsKeeper(start_time)
#     pitch_keeper = kk.KinematicsKeeper(start_time)
#     roll_keeper = kk.KinematicsKeeper(start_time)
#     yaw_keeper = kk.KinematicsKeeper(start_time)
    for accel_point in accel_points:
        new_time = accel_point[0]
        surge_keeper.generate_next_state(new_time, accel_point[1])
        sway_keeper.generate_next_state(new_time, accel_point[2])
        heave_keeper.generate_next_state(new_time, accel_point[3])
        next_excursions = [surge_keeper.get_excursion(), sway_keeper.get_excursion(), heave_keeper.get_excursion()]
        raw_excursion_sets.append(next_excursions)
    return raw_excursion_sets
        