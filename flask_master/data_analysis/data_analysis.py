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
import time
from astropy.units import one

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

def _comparator(element):
    return element[0]

def process_accelerations(start, end, interval, points):
    start_time = time.time()
    dc.getcontext().prec = 6
    zero = dc.Decimal(0.0)
    one = dc.Decimal(1.0)
    interval_d = dc.Decimal(interval) * one
    start_d = dc.Decimal(start) * one
    end_d = dc.Decimal(end) * one
    real_end_d = start_d + (end_d // interval_d) * interval_d
    end_index = determine_end(points, real_end_d)
    start_index = determine_start(points, start_d, end_index)
    points = points[start_index:end_index]
    final_points = []
    final_points.append([start, 0.0, 0.0, 0.0])
    points.append([float(real_end_d), 0.0, 0.0, 0.0])
    end_time = time.time()
    print(end_time - start_time)
    n = 0
    z = 0
    while(True):
        if(n >= len(points)):
            return final_points
        curr_point = final_points[z]
        next_point = points[n]
        time_diff = dc.Decimal(next_point[0]) * one - dc.Decimal(curr_point[0]) * one
        if (time_diff == zero):
            final_points[z] = next_point
        elif (time_diff == interval_d):
            final_points.append(next_point)
            z = z + 1
        elif (time_diff > zero and time_diff > interval_d):
            raw_ratio = time_diff / interval_d
            num_elements = math.floor(raw_ratio)
            last_time = (dc.Decimal(curr_point[0]) * one) + (num_elements * interval_d)
            time_ratio = last_time / dc.Decimal(next_point[0])
            fv1 = float(((dc.Decimal(next_point[1]) * time_ratio) - dc.Decimal(curr_point[1])) / num_elements)
            fv2 = float(((dc.Decimal(next_point[2]) * time_ratio) - dc.Decimal(curr_point[2])) / num_elements)
            fv3 = float(((dc.Decimal(next_point[3]) * time_ratio) - dc.Decimal(curr_point[3])) / num_elements)
            while(True):
                next_time = dc.Decimal(curr_point[0]) * dc.Decimal(1.0) + interval_d
                if(next_time > last_time):
                    break
                curr_point = [float(next_time), curr_point[1] + fv1, curr_point[2] + fv2, curr_point[3] + fv3]
                final_points.append(curr_point)
            z = len(final_points) - 1
        n = n + 1

def determine_end(points, real_end):
    one = dc.Decimal(1.0)
    end_index = len(points) - 1
    while(end_index >= 0):
        curr_comparison = dc.Decimal(points[end_index][0]) * one
        if(curr_comparison <= real_end):
            break
        end_index = end_index - 1
    return end_index + 1

def determine_start(points, start, end_index):
    one = dc.Decimal(1.0)
    start_index = 0
    while(start_index <= end_index):
        if(start_index >= len(points)):
            return end_index
        curr_comparison = dc.Decimal(points[start_index][0]) * one
        if(curr_comparison > start):
            break
        start_index = start_index + 1
    return start_index

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
        