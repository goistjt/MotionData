"""
Created on Oct 15, 2016

@author: yangr
"""
import pandas as pd
import numpy as np

from flask_master.database import crud

import flask_master.data_analysis.kinematics_keeper as kk
import flask_master.data_analysis.max_collection_factories as mcf

def select_record(records_id):
    query = "SELECT GyroPoints.roll, GyroPoints.pitch, GyroPoints.yaw, AccessPoints.surge, AccessPoints.sway, AccessPoints.heave " \
            "FROM GyroPoints INNER JOIN AccessPoints " \
            "ON GyroPoints.record_id = %s " \
            "AND GyroPoints.timestamp = AccessPoints.timestamp " \
            "ORDER BY GyroPoints.timestamp ASC"
    args = [records_id]
    return crud.read_all(query, args)


def download_record(record_id = []):
    df = pd.DataFrame(np.array(select_record(record_id)))
    return df.to_csv(index=False)

def get_excursions(start_time, accel_points, gyro_points):
    max_collection_factory = mcf.MaxCollectionFactory()
    raw_excursion_sets = np.array([[0, 0, 0, 0, 0, 0]])
    surge_keeper = kk.KinematicsKeeper(start_time, max_collection_factory.createMaxCollection(0))
    sway_keeper = kk.KinematicsKeeper(start_time, max_collection_factory.createMaxCollection(1))
    heave_keeper = kk.KinematicsKeeper(start_time, max_collection_factory.createMaxCollection(2))
    pitch_keeper = kk.KinematicsKeeper(start_time, max_collection_factory.createMaxCollection(3))
    roll_keeper = kk.KinematicsKeeper(start_time, max_collection_factory.createMaxCollection(4))
    yaw_keeper = kk.KinematicsKeeper(start_time, max_collection_factory.createMaxCollection(5))
    x = 0
    while (x < len(accel_points) and x < len(gyro_points)):
        accel_point = accel_points[x]
        gyro_point = gyro_points[x]
        new_time = accel_point[0]
        surge_keeper.generate_next_state(new_time, accel_point[1])
        sway_keeper.generate_next_state(new_time, accel_point[2])
        heave_keeper.generate_next_state(new_time, accel_point[3])
        pitch_keeper.generate_next_state(new_time, gyro_point[1])
        roll_keeper.generate_next_state(new_time, gyro_point[2])
        yaw_keeper.generate_next_state(new_time, gyro_point[3])
        next_excursions = [surge_keeper.get_excursion(), sway_keeper.get_excursion(), heave_keeper.get_excursion(), pitch_keeper.get_excursion(), roll_keeper.get_excursion(), yaw_keeper.get_excursion()]
        raw_excursion_sets = np.append(raw_excursion_sets, np.array([next_excursions]), axis=0)
        x = x + 1
    return raw_excursion_sets
        