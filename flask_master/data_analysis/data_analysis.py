"""
Created on Oct 15, 2016

@author: yangr
"""
import pandas as pd
import numpy as np
import decimal as dc
import math
from flask_server import crud

import data_analysis.kinematics_keeper as kk
import data_analysis.max_collection_factories as mcf


def select_record(record_id):
    return crud.get_record(record_id)


def download_record_raw(record_id=[]):
    accel_base = list(crud.select_accel(record_id))
    gyro_base = crud.select_gyro(record_id)

    start = gyro_base[0][0] if gyro_base[0][0] > accel_base[0][0] else accel_base[0][0]
    # sync start times for the accel & gyro data
    if len(accel_base) > 1:
        while accel_base[1][0] < start:
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
    return df.to_csv(index=False, header=False)


def download_record_analyzed(record_id=[]):
    # TODO : update this to actually analyze the selected data
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


def clean_session(start_time, end_time, accel_points, gyro_points):
    
    interval = 40
    
    if(start_time >= end_time):
        return []
    
    accel_list = process_accelerations(start_time, end_time, interval, accel_points)
    
    gyro_list = process_accelerations(start_time, end_time, interval, gyro_points)
    
    if((accel_list == None or len(accel_list) == 0) or (gyro_list == None or len(gyro_list) == 0) or (len(gyro_list) != len(accel_list))):
        return []
    
    maxCF = mcf.MaxCollectionFactory()
    
    surge_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.SURGE))
    sway_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.SWAY))
    heave_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.HEAVE))
    
    keeps_accel = [surge_keeper, sway_keeper, heave_keeper]
    
    roll_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.ROLL))
    pitch_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.PITCH))
    yaw_keeper = kk.KinematicsKeeper(start_time, maxCF.createMaxCollection(maxCF.YAW))
    
    keeps_gyro = [roll_keeper, pitch_keeper, yaw_keeper]
    
    session = []
    
    for i in range(len(gyro_list)):
        
        next_set = []
        
        next_set = process_normal_state_generations(keeps_accel, accel_list, i, next_set)
        
        next_set = process_normal_state_generations(keeps_gyro, gyro_list, i, next_set)
        
        session.append(next_set)
        
    return process_return_to_zero(end_time, interval, keeps_accel, keeps_gyro, session)


def process_normal_state_generations(keeps_list, values_list, position, next_set):
    
    for x in range(len(keeps_list)):
        time_val = values_list[position][0]
        accel_val = values_list[position][x + 1]
        curr_keep = keeps_list[x]
        curr_keep.generate_next_state(time_val, accel_val)
        next_set.append(curr_keep.get_position())
    
    return next_set


def process_return_to_zero(end_time, interval, keeps_accel, keeps_gyro, session):
    
    acc_time = end_time
    
    while(True):
        
        acc_time += interval
        
        next_set = []
        
        next_set = process_for_next_set(keeps_accel, acc_time, next_set)
        
        next_set = process_for_next_set(keeps_gyro, acc_time, next_set)
        
        if(np.allclose(next_set, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 0.0000001)):
            next_set = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            session.append(next_set)
            break;
        
        session.append(next_set)
        
    return session

def process_for_next_set(keeps_list, acc_time, next_set):
    
    for o in range(len(keeps_list)):
        
        curr_keep = keeps_list[o]
        pos = curr_keep.get_position()
        
        if(pos == 0.0):
            
            next_set.append(0.0)
            
        else:
            
            if(pos > 0):
                accel_val = -curr_keep.get_max_acceleration() / 2
            
            else:
                accel_val = curr_keep.get_max_acceleration() / 2
            
            curr_keep.generate_next_state(acc_time, accel_val)
            
            pos_next = curr_keep.get_position()
            
            if(pos_next == 0.0 or (pos_next / abs(pos_next)) != (pos / (abs(pos)))):
                curr_keep.set_position(0.0)
                next_set.append(0.0)
            
            else:
                next_set.append(curr_keep.get_position())
            
    return next_set