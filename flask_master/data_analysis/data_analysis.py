"""
Created on Oct 15, 2016

@author: yangr
"""
import decimal as dc
import math

import numpy as np
import pandas as pd

import data_analysis.kinematics_keeper as kk
import data_analysis.max_collection_factories as mcf
from flask_server import crud


def select_record(records_id):
    query = "SELECT GyroPoints.roll, GyroPoints.pitch, GyroPoints.yaw, AccelPoints.surge, AccelPoints.sway, " \
            "AccelPoints.heave " \
            "FROM GyroPoints INNER JOIN AccelPoints " \
            "ON GyroPoints.record_id = %s " \
            "AND GyroPoints.timestamp = AccelPoints.timestamp " \
            "ORDER BY GyroPoints.timestamp ASC"
    args = [records_id]
    return crud.read_all(query, args)


def download_record_raw(record_id):
    accel_base = crud.select_accel(record_id)
    gyro_base = crud.select_gyro(record_id)
    return point_alignment(accel_base, gyro_base)


def point_alignment(accel_base, gyro_base):
    accel_base = list(accel_base)
    gyro_base = list(gyro_base)
    start = gyro_base[0][0] if gyro_base[0][0] > accel_base[0][0] else accel_base[0][0]
    # sync start times for the accel & gyro data

    while len(accel_base) > 1 and accel_base[1][0] < start:
        accel_base.pop(0)

    accel = []
    for p in accel_base:
        point = [p[1], p[2], p[3]]
        accel.append(point)
    gyro = []
    for p in gyro_base:
        point = [p[1], p[2], p[3]]
        gyro.append(point)

    points = []
    i = 0
    j = len(gyro) if len(gyro) < len(accel) else len(accel)
    zeropoint = [0, 0, 0, 0, 0, 0]
    points.append(zeropoint)
    while i < j:
        point = []
        for p in accel[i]:
            point.append(p)
        for p in gyro[i]:
            point.append(p)
        points.append(point)
        i += 1
    points.append(zeropoint)

    df = pd.DataFrame(np.array(points))
    return df.to_csv(index=False, header=False, sep=" ", float_format="%.6f")


def download_record_analyzed(record_id):
    # TODO: Replace some of the below code with calls to Runzhi's new procedures / functions
    accel_base = list(crud.select_accel(record_id))
    gyro_base = list(crud.select_gyro(record_id))

    start = 0
    end = 0

    if ((gyro_base is not None) and (len(gyro_base) > 1)) and ((accel_base is not None) and len(accel_base)):
        start = max(accel_base[0][0], gyro_base[0][0])
        end = min(accel_base[len(accel_base) - 1][0], gyro_base[len(gyro_base) - 1][0])

    df = pd.DataFrame(np.array(generate_processed_data(start, end, accel_base, gyro_base, 40)))

    return df.to_csv(index=False, header=False, sep=" ", float_format='%.6f')


def download_session_raw(session_id):
    records = crud.get_all_records_from_session(session_id)
    record_accel_data = []
    record_gyro_data = []
    for record in records:
        record_accel_data.append(crud.select_accel(record[0]))
        record_gyro_data.append(crud.select_gyro(record[0]))
    avg_accel = average_timeseries_data(record_accel_data)
    avg_gyro = average_timeseries_data(record_gyro_data)
    return point_alignment(avg_accel, avg_gyro)


def average_timeseries_data(records, iteration=1):
    if len(records) == 1:
        return records[0]

    record1 = list(records.pop(0))
    record2 = list(records.pop(0))
    record_avg = []

    while len(record1) > 0 and len(record2) > 0:
        while record1[0] < record2[0]:
            record_avg.append(record1.pop(0))

        rec1 = record1.pop(0)
        rec2 = record2.pop(0)[1:]
        r_avg = [rec1[0]]
        rec1 = rec1[1:]
        for r1, r2 in zip(rec1, rec2):
            r_avg.append(((r1 * iteration) + r2) / (iteration + 1))

        record_avg.append(r_avg)

    while len(record1) > 0:
        record_avg.append(record1.pop(0))

    while len(record2) > 0:
        record_avg.append(record2.pop(0))

    rec_copy = records
    rec_copy.insert(0, record_avg)
    return average_timeseries_data(rec_copy, iteration + 1)


def download_session_analyzed(session_id=[]):
    if session_id is None:
        session_id = []

    accel_base = list(crud.get_all_accel_points_from_session(session_id))
    gyro_base = list(crud.get_all_gyro_points_from_session(session_id))

    print(accel_base)
    print(gyro_base)

    start = 0
    end = 0

    if ((gyro_base is not None) and (len(gyro_base) > 1)) and ((accel_base is not None) and len(accel_base)):
        start = max(accel_base[0][0], gyro_base[0][0])
        end = min(accel_base[len(accel_base) - 1][0], gyro_base[len(gyro_base) - 1][0])

    df = pd.DataFrame(np.array(generate_processed_data(start, end, accel_base, gyro_base, 40)))

    return df.to_csv(index=False, header=False, sep=" ", float_format='%.6f')


def process_accelerations(start, end, interval, points):
    # Sets the precision level for operations referencing the Decimal datatype
    dc.getcontext().prec = 20
    # Default one and zero values
    zero = dc.Decimal(0.0)
    one = dc.Decimal(1.0)

    interval_d = dc.Decimal(interval) * one
    start_d = dc.Decimal(start) * one
    end_d = dc.Decimal(end) * one
    real_end_d = start_d + ((end_d - start_d) // interval_d) * interval_d
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
        time_diff = (dc.Decimal(next_point[0]) * one) - (dc.Decimal(curr_point[0]) * one)

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


def generate_processed_data(start_time, end_time, accel_points, gyro_points, interval):

    default_list = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]

    if start_time >= end_time:
        return default_list

    accel_list = process_accelerations(start_time, end_time, interval, accel_points)

    gyro_list = process_accelerations(start_time, end_time, interval, gyro_points)

    if ((accel_list is None or len(accel_list) == 0) or (gyro_list is None or len(gyro_list) == 0) or (
                len(gyro_list) != len(accel_list))):
        return default_list

    max_coll_fact = mcf.MaxCollectionFactory()

    buffer_factor = 0.85
    surge_keeper = kk.KinematicsKeeper(max_coll_fact.create_max_collection(max_coll_fact.SURGE), buffer_factor)
    sway_keeper = kk.KinematicsKeeper(max_coll_fact.create_max_collection(max_coll_fact.SWAY), buffer_factor)
    heave_keeper = kk.KinematicsKeeper(max_coll_fact.create_max_collection(max_coll_fact.HEAVE), buffer_factor)

    keeps_accel = [surge_keeper, sway_keeper, heave_keeper]

    roll_keeper = kk.KinematicsKeeper(max_coll_fact.create_max_collection(max_coll_fact.ROLL), buffer_factor)
    pitch_keeper = kk.KinematicsKeeper(max_coll_fact.create_max_collection(max_coll_fact.PITCH), buffer_factor)
    yaw_keeper = kk.KinematicsKeeper(max_coll_fact.create_max_collection(max_coll_fact.YAW), buffer_factor)

    keeps_gyro = [roll_keeper, pitch_keeper, yaw_keeper]

    session = []

    for i in range(len(gyro_list)):

        next_set = []

        next_set = process_states(keeps_accel, accel_list, i, next_set, kk.KinematicsKeeper.ACCELERATION)

        next_set = process_states(keeps_gyro, gyro_list, i, next_set, kk.KinematicsKeeper.VELOCITY)

        session.append(next_set)

    return process_return_to_zero(keeps_accel, keeps_gyro, session)


def process_states(keeps_list, values_list, position, next_set, starting_value_type):

    for x in range(len(keeps_list)):

        val = values_list[position][x + 1]

        curr_keep = keeps_list[x]

        curr_keep.generate_next_state(val, starting_value_type)

        next_set.append(curr_keep.get_position())

    return next_set


def process_return_to_zero(keeps_accel, keeps_gyro, session):

    while True:

        next_set = []

        next_set = process_for_next_set(keeps_accel, next_set)

        next_set = process_for_next_set(keeps_gyro, next_set)

        if np.allclose(next_set, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], atol=0.0000001):
            next_set = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            session.append(next_set)
            break

        session.append(next_set)

    return session


def process_for_next_set(keeps_list, next_set):

    # TODO: Could very much move things like this into a configuration file or make the data analysis class instantiated
    maximum_buffer_factor = 0.5

    for x in range(len(keeps_list)):

        curr_keep = keeps_list[x]
        pos = curr_keep.get_position()

        if pos == 0.0:
            next_set.append(0.0)
            continue

        elif pos > 0:
            accel_val = -curr_keep.get_max_acceleration() * maximum_buffer_factor

        else:
            accel_val = curr_keep.get_max_acceleration() * maximum_buffer_factor

        curr_keep.generate_next_state(accel_val, kk.KinematicsKeeper.ACCELERATION)

        pos_next = curr_keep.get_position()

        if (abs(pos_next - 0.0) < 0.0000001) or ((pos_next / abs(pos_next)) != (pos / (abs(pos)))):
            curr_keep.set_position(0.0)
            next_set.append(0.0)
            continue

        next_set.append(curr_keep.get_position())

    return next_set
