"""
Created on Oct 15, 2016

@author: yangr
"""
import pandas as pd
import numpy as np

from database import crud

import data_analysis.kinematics_keeper as kk
import data_analysis.max_collection_factories as mcf
import data_analysis.max_collections as mc
import decimal as dc

import math

def set_up_factories():
    maxColFact = mcf.MaxCollectionFactory()
    maxColFact.addFactory(0, mc.SurgeCollection)
    maxColFact.addFactory(1, mc.SwayCollection)
    maxColFact.addFactory(2, mc.HeaveCollection)
    maxColFact.addFactory(3, mc.RollCollection)
    maxColFact.addFactory(4, mc.PitchCollection)
    maxColFact.addFactory(5, mc.YawCollection)
    return maxColFact

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

def process_accelerations(start, end, interval, points):
    dc.getcontext().prec = 6
    one = dc.Decimal(1.0)
    zero = dc.Decimal(0.0)
    interval_d = dc.Decimal(interval) * dc.Decimal(1.0)
    start_d = dc.Decimal(start) * dc.Decimal(1.0)
    end_d = dc.Decimal(end) * dc.Decimal(1.0)
    real_end_d = (end_d // interval_d) * interval_d
    total_diff = end_d - start_d
    total_elements = math.floor(dc.Decimal(total_diff / interval_d)) + 1
    end_index = len(points) - 1
    while(end_index >= 0):
        curr_comparison = dc.Decimal(points[end_index][0]) * one
        if(curr_comparison <= real_end_d):
            break
        end_index = end_index - 1
    start_index = 0
    while(start_index <= end_index):
        curr_comparison = dc.Decimal(points[start_index][0]) * one
        if(curr_comparison >= start_d):
            break
        start_index = start_index + 1
    points = points[start_index:end_index]
    points[0] = np.array([start, 0.0, 0.0, 0.0])
    points = np.append(points, np.array([[float(real_end_d), 0.0, 0.0, 0.0]]), axis=0)
    print(points)
    n = 0
    while(True):
        if(n + 1 == len(points)):
            return points[:total_elements]
        time_diff = dc.Decimal(points[n + 1][0]) - dc.Decimal(points[n][0])
        if (time_diff < zero):
            points = np.delete(points, n + 1, 0)
        elif (time_diff == zero):
            points = np.delete(points, n, 0)
        elif (time_diff < interval_d):
            points = np.delete(points, n + 1, 0)
        elif (time_diff == interval_d):
            n = n + 1
        else:
            curr_point = points[n]
            next_point = points[n + 1]
            raw_ratio = time_diff / interval_d
            num_elements = math.floor(raw_ratio)
            cp1 = dc.Decimal(curr_point[1])
            cp2 = dc.Decimal(curr_point[2])
            cp3 = dc.Decimal(curr_point[3])
            next_one = (cp1 + (dc.Decimal(next_point[1]) - cp1) * (num_elements / raw_ratio))
            next_two = (cp2 + (dc.Decimal(next_point[2]) - cp2) * (num_elements / raw_ratio))
            next_three = (cp3 + (dc.Decimal(next_point[3]) - cp3) * (num_elements / raw_ratio))
            fv1 = (next_one - cp1) / num_elements
            fv2 = (next_two - cp2) / num_elements
            fv3 = (next_three - cp3) / num_elements
            points = np.delete(points, n + 1, 0)
            fv1 = float(fv1)
            fv2 = float(fv2)
            fv3 = float(fv3)
            while(num_elements > 0):
                points = np.insert(points, n + 1, [points[n][0] + interval, points[n][1] + fv1, points[n][2] + fv2, points[n][3] + fv3], axis=0)
                num_elements = num_elements - 1
                if(num_elements != 0):
                    n = n + 1

def get_excursions(start_time, accel_points, gyro_points):
    max_collection_factory = set_up_factories()
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
        