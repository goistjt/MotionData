"""
Created on Oct 15, 2016

@author: yangr
"""
import pandas as pd
import numpy as np
import decimal as dc
import math

from database import crud

"""
import data_analysis.kinematics_keeper as kk
import data_analysis.max_collection_factories as mcf
"""


def select_record(records_id):
    query = "SELECT GyroPoints.roll, GyroPoints.pitch, GyroPoints.yaw, AccelPoints.surge, AccelPoints.sway, " \
            "AccelPoints.heave " \
            "FROM GyroPoints INNER JOIN AccelPoints " \
            "ON GyroPoints.record_id = %s " \
            "AND GyroPoints.timestamp = AccelPoints.timestamp " \
            "ORDER BY GyroPoints.timestamp ASC"
    args = [records_id]
    return crud.read_all(query, args)


def download_record(record_id=[]):
    df = pd.DataFrame(np.array(select_record(record_id)))
    return df.to_csv(index=False)


def process_accelerations(start, end, interval, points):
    # Sets the precision level for operations referencing the Decimal datatype
    dc.getcontext().prec = 6

    # Default one and zero values
    zero = dc.Decimal(0.0)
    one = dc.Decimal(1.0)

    interval_d = dc.Decimal(interval) * one

    start_d = dc.Decimal(start) * one
    end_d = dc.Decimal(end) * one

    real_end_d = start_d + (end_d // interval_d) * interval_d

    end_index = determine_end(points, real_end_d)
    start_index = determine_start(points, start_d, end_index)

    points = points[start_index:end_index]

    final_points = [[start, 0.0, 0.0, 0.0]]

    points.append([float(real_end_d), 0.0, 0.0, 0.0])

    n = 0
    z = 0
    while True:
        # At end of original
        if n >= len(points):
            return final_points

        curr_point = final_points[z]
        next_point = points[n]

        # Current time difference
        time_diff = dc.Decimal(next_point[0]) * one - dc.Decimal(curr_point[0]) * one

        if time_diff == zero:
            final_points[z] = next_point

        elif time_diff == interval_d:
            final_points.append(next_point)
            z += 1

        elif time_diff > zero and time_diff > interval_d:
            raw_ratio = time_diff / interval_d
            num_elements = math.floor(raw_ratio)

            last_time = (dc.Decimal(curr_point[0]) * one) + (num_elements * interval_d)
            time_ratio = last_time / dc.Decimal(next_point[0])

            fv1 = float(((dc.Decimal(next_point[1]) * time_ratio) - dc.Decimal(curr_point[1])) / num_elements)
            fv2 = float(((dc.Decimal(next_point[2]) * time_ratio) - dc.Decimal(curr_point[2])) / num_elements)
            fv3 = float(((dc.Decimal(next_point[3]) * time_ratio) - dc.Decimal(curr_point[3])) / num_elements)

            while True:
                next_time = dc.Decimal(curr_point[0]) * dc.Decimal(1.0) + interval_d
                if next_time > last_time:
                    break
                curr_point = [float(next_time), curr_point[1] + fv1, curr_point[2] + fv2, curr_point[3] + fv3]
                final_points.append(curr_point)

            z = len(final_points) - 1

        n += 1


def determine_end(points, real_end):
    one = dc.Decimal(1.0)
    end_index = len(points) - 1
    while end_index >= 0:
        curr_comparison = dc.Decimal(points[end_index][0]) * one
        if curr_comparison <= real_end:
            break
        end_index -= 1
    return end_index + 1


def determine_start(points, start, end_index):
    one = dc.Decimal(1.0)
    start_index = 0
    while start_index <= end_index:
        if start_index >= len(points):
            return end_index
        curr_comparison = dc.Decimal(points[start_index][0]) * one
        if curr_comparison > start:
            break
        start_index += 1
    return start_index


def get_excursions(start_time, end_time, accel_points, gyro_points):
    raw_excursion_sets = np.array([[0, 0, 0, 0, 0, 0]])

    """
    maxCF = mcf.MaxCollectionFactory()
    surge_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.SURGE))
    sway_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.SWAY))
    heave_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.HEAVE))
    pitch_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.ROLL))
    roll_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.PITCH))
    yaw_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.YAW))
    """

    interval = 0.04
    accel_points = process_accelerations(start_time, end_time, interval, accel_points)
    gyro_points = process_accelerations(start_time, end_time, interval, gyro_points)

    return raw_excursion_sets
