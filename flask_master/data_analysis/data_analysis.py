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

    interval = 40

    if record_id is None:
        return None

    accel_base = list(crud.select_accel(record_id))
    gyro_base = list(crud.select_gyro(record_id))

    start = 0
    end = 0

    if ((gyro_base is not None) and len(gyro_base)) and ((accel_base is not None) and len(accel_base)):

        if (gyro_base[0][0] is None) or (accel_base[0][0] is None) or (accel_base[len(accel_base) - 1][0] is None) or (
                    gyro_base[len(gyro_base) - 1][0] is None):
            return (pd.DataFrame(np.array([]))).to_csv(index=False, header=False, sep=" ", float_format='%.6f')

        start = max(accel_base[0][0], gyro_base[0][0]) - interval
        end = min(accel_base[len(accel_base) - 1][0], gyro_base[len(gyro_base) - 1][0]) + interval

    df = pd.DataFrame(np.array(generate_processed_data(start, end, accel_base, gyro_base, interval)))

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

    interval = 40

    if session_id is None:
        return (pd.DataFrame(np.array([]))).to_csv(index=False, header=False, sep=" ", float_format='%.6f')

    accel_base = list(crud.get_all_accel_points_from_session(session_id))
    gyro_base = list(crud.get_all_gyro_points_from_session(session_id))

    start = 0
    end = 0

    if ((gyro_base is not None) and len(gyro_base)) and ((accel_base is not None) and len(accel_base)):

        if (gyro_base[0][0] is None) or (accel_base[0][0] is None) or (accel_base[len(accel_base) - 1][0] is None) or (
                    gyro_base[len(gyro_base) - 1][0] is None):
            return (pd.DataFrame(np.array([]))).to_csv(index=False, header=False, sep=" ", float_format='%.6f')

        start = max(accel_base[0][0], gyro_base[0][0]) - interval
        end = min(accel_base[len(accel_base) - 1][0], gyro_base[len(gyro_base) - 1][0]) + interval

    df = pd.DataFrame(np.array(generate_processed_data(start, end, accel_base, gyro_base, interval)))

    return df.to_csv(index=False, header=False, sep=" ", float_format='%.6f')


def process_accelerations(start, end, interval, points):
    """
    The main preprocessing function in charge of transforming raw accelerations and timestamps into uniformed and matching
    accelerations for each expected interval.

    Params: start - time in milliseconds
            end - time in milliseconds
            interval - time between points in milliseconds
            points - the original sequence of accelerations

    Returns: final_points - a sequence of preprocessed accelerations for future use

    """

    # Sets the precision level for operations referencing the Decimal datatype
    dc.getcontext().prec = 20

    # Max distance between two collected points' times.
    max_time_diff = 120000

    # Default one and zero values
    ZERO = dc.Decimal(0.0)
    ONE = dc.Decimal(1.0)

    # Converting intervals and start times to Decimals
    interval_d = dc.Decimal(interval) * ONE
    start_d = dc.Decimal(start) * ONE
    end_d = dc.Decimal(end) * ONE

    # Finding the ending interval based on interval and time difference from start
    real_end_d = start_d + ((end_d - start_d) // interval_d) * interval_d

    # Potentially cutting off beginning and end based on start and end times
    end_index = determine_end(points, real_end_d)
    start_index = determine_start(points, start_d, end_index)

    points = points[start_index:end_index]

    final_points = [[start, 0.0, 0.0, 0.0]]

    points.append([float(real_end_d), 0.0, 0.0, 0.0])

    for next_point in points:

        if dc.Decimal(next_point[0]) * ONE > end_d:
            return final_points, end

        curr_point = final_points[len(final_points) - 1]

        # Current time difference
        time_diff = (dc.Decimal(next_point[0]) * ONE) - (dc.Decimal(curr_point[0]) * ONE)

        if time_diff > max_time_diff:
            return final_points, next_point[0]

        elif time_diff == ZERO:
            final_points[len(final_points) - 1] = next_point

        elif time_diff == interval_d:
            final_points.append(next_point)

        elif time_diff > ZERO and time_diff > interval_d:

            raw_ratio = time_diff / interval_d
            num_elements = math.floor(raw_ratio)

            last_time = (dc.Decimal(curr_point[0]) * ONE) + (num_elements * interval_d)
            time_ratio = last_time / dc.Decimal(next_point[0])

            fv1 = float(((dc.Decimal(next_point[1]) * time_ratio) - dc.Decimal(curr_point[1])) / num_elements)
            fv2 = float(((dc.Decimal(next_point[2]) * time_ratio) - dc.Decimal(curr_point[2])) / num_elements)
            fv3 = float(((dc.Decimal(next_point[3]) * time_ratio) - dc.Decimal(curr_point[3])) / num_elements)

            i = 0

            while True:

                next_time = dc.Decimal(curr_point[0]) * dc.Decimal(1.0) + interval_d

                if next_time > last_time or next_time > end_d:
                    break

                curr_point = [float(next_time), curr_point[1] + fv1, curr_point[2] + fv2, curr_point[3] + fv3]

                final_points.append(curr_point)

                i += 1

    return final_points, end


def determine_end(points, real_end):
    """
    Determines the correct ending time of the data provided in order to ensure a logical start to the series before
    preprocessing begins.

    Params: points - original points contianing their assocaited times
            real_end - the max end time desired

    Returns: the index of the final point before or equal to the end time
    """

    ONE = dc.Decimal(1.0)

    end_index = len(points) - 1

    while end_index >= 0:

        if points[end_index][0] is None:
            return end_index

        curr_comparison = dc.Decimal(points[end_index][0]) * ONE

        if curr_comparison <= real_end:
            break

        end_index -= 1

    return end_index + 1


def determine_start(points, start, end_index):
    """
    Determines the correct starting time of the data provided in order to ensure a logical start to the series before
    preprocessing begins.

    Params: points - accelerations and their times
            end_index - the predetermined end index for this list of points
            start - the desired max start time

    Returns: starting index of the set of points for the given time
    """

    ONE = dc.Decimal(1.0)
    start_index = 0

    while start_index <= end_index:

        if points[start_index][0] is None:
            return start_index

        if start_index >= len(points):
            return end_index

        curr_comparison = dc.Decimal(points[start_index][0]) * ONE

        if curr_comparison > start:
            break

        start_index += 1

    return start_index


def generate_processed_data(start_time, end_time, accel_points, gyro_points, interval):
    """
    The main "state machine" used to generate the processed positional data from the preprocessed acceleration data derived
    from the raw collected data. The output of this function should serve as the content of the simulation file.

    Params: start_time - initial time for total series
            end_time - ending time for total series
            accel_points - the original sequence of acceleration points
                           in this format - [ <timestamp>, <surge>, <sway>, <heave> ]
            gyro_points - the original sequence of gyroscope points
                          in this format - [ <timestamp>, <roll>, <pitch>, <yaw> ]
            interval - the time, in milliseconds, between each entry in the final set / playback interval
    """

    default_list = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]

    if start_time >= end_time:
        return default_list

    accel_list, end_time = process_accelerations(start_time, end_time, interval, accel_points)

    gyro_list, end_time = process_accelerations(start_time, end_time, interval, gyro_points)

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

        next_set = process_states(keeps_accel, accel_list[i], next_set, kk.KinematicsKeeper.ACCELERATION)

        next_set = process_states(keeps_gyro, gyro_list[i], next_set, kk.KinematicsKeeper.VELOCITY)

        session.append(next_set)

    return process_return_to_zero(keeps_accel, keeps_gyro, session)


def process_states(keeps_list, point, next_set, starting_value_type):
    """
    For each degree of freedom in the list specified and for the starting position specified, will generate the next
    state of the keeper associated and append the new position for the set for a particular interval / time.

    Params: keeps_list - the list of KinematicsKeepers we want to iterate through / generate state from
            point - the point containing what will be inputs to the KinematicsKeepers
            next_set - the set to append the results of the state generation to
            starting_value_type - the type of value the point is containing as inputs - acceleration, velocity, or
                                  position, this should be one of the constants from the KinematicsKeeper class
    """

    for x in range(len(keeps_list)):
        val = point[x + 1]

        curr_keep = keeps_list[x]

        curr_keep.generate_next_state(val, starting_value_type)

        next_set.append(curr_keep.get_position())

    return next_set


def process_return_to_zero(keeps_accel, keeps_gyro, session):
    """
    Modifies the existing session generated under normal inputs to extend until all values have reached zero position. Uses
    process_for_next_set to generate the next closest states to zero for each of the degrees of motion.

    Params: keeps_accel - the keepers for the accelerometer-based degrees of freedom
            keeps_gyro - the keepers for the gyroscope-based degrees of freedom
            session - the pre-generated data set determined from the processing of collected accelerations
                      and angular velocities. This set is the one that needs to be returned to zero position.

    Returns: the input processed data set returned to zero position.
    """

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
    """
    For each KinematicsKeeper (for each degree of freedom), check if the current values are zeroed to original status, and
    if not generate the next state closer to zero by half the maximum acceleration specified by the keeper. This is a helper
    function in order to drive all keepers to zero.

    Params: keeps_list - the set of KinematicsKeepers to be iterated through to produce generated state values from
            next_set - the set to append the current six degrees' states to for addition to the total session

    Returns: next_set - the original set given for this time, plus the appended generated values for these keepers.

    """

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
