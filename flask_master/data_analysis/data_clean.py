'''
Created on Jan 18, 2017

@author: yangr
'''
import numpy as np
import pandas as pd

class Data_clean():
    '''
    Warning, for integer matrix, expect to cast into float matrix first 
    before perform analysis
    ''' 
    def __init__(self):
        self.accel_s = 1
        self.accel_e = 4
        self.gyro_s = 4
        self.gyro_e = 7
        

    def clean_data_by_averaging(self, data):
        accel_processed = 0
        gyro_processed = 0
        total_row = data.shape[0]
        # skipping the first and last row since the machine starts at 0 and ends at 0
        for row_num in range(total_row):
            if row_num > accel_processed and self.is_empty_record(self.accel_s, self.accel_e, data[row_num]):
                (accel_processed, data) = self.average_Neighbors(row_num, self.accel_s, self.accel_e, data)
            if row_num > gyro_processed and self.is_empty_record(self.gyro_s, self.gyro_e, data[row_num]):
                (gyro_processed, data) = self.average_Neighbors(row_num, self.gyro_s, self.gyro_e, data)
        return data

    def is_empty_record(self, s_col, e_col, array):
        return not np.any(array[0, s_col:e_col])
    
    # This starts the average neighboring process, 
    # and find the next point that has a value
    def average_Neighbors(self, row_num, s_col, e_col, data):
        cur = row_num
        while cur< data.shape[0] and self.is_empty_record(s_col, e_col, data[cur]):
            cur = cur + 1
            
        if cur + 1 == data.shape[0]:
            data = self.fill_forward_in_time(row_num, cur, s_col, e_col, data)
        elif row_num == 1:
            data = self.fill_back_in_time(row_num, cur, s_col, e_col, data)
        else:
            data = self.fill_inbetween_time(row_num, cur, s_col, e_col, data)
        return (cur + 1, data)
    
    def fill_forward_in_time(self, s_t, e_t, s_col, e_col, data):
        time_interval = e_t - s_t + 1
        # Form an array of changes
        change = np.squeeze(np.asarray((data[s_t - 1, s_col:e_col] / time_interval)))
        for row in range(s_t , e_t + 1):
            data[row, s_col:e_col] = np.subtract(data[row - 1, s_col:e_col], change)
        return data
    
#     Starting time is the first empty cell, ending time is the first cell contains data
    def fill_back_in_time(self, s_t, e_t, s_col, e_col, data):
        time_interval = e_t - s_t + 1
        change = np.squeeze(np.asarray((data[e_t, s_col:e_col] / time_interval)))
        for row in range(e_t - 1, s_t - 1, -1):
            data[row, s_col:e_col] = np.subtract(data[row + 1, s_col:e_col], change)
        return data
    
    def fill_inbetween_time(self, s_t, e_t, s_col, e_col, data):
        time_interval = e_t - s_t
        change = np.squeeze(np.asarray(np.subtract(data[e_t, s_col:e_col], data[s_t, s_col:e_col]))) / time_interval
        for row in range(s_t + 1, e_t):
            data[row, s_col:e_col] = np.add(data[row - 1, s_col:e_col], change)
        return data
            
    def sync_thresholds(self, data, columns=7, threshold=0.04):
#         data = np.subtract(data[:,0], data[0,0])
        output = np.zeros(columns)
        current_base, end = 0, data.shape[0]
        current_range = current_base + threshold
        new_timestamp = threshold
        for current_row in range(end):
            if data[current_row, 0] >= current_range or current_row == end - 1:
#                 This line checks when there is no data within the sync thresholds
                while data[current_base, 0] > current_range:
                    new_time_value = np.hstack((new_timestamp, np.zeros(columns - 1)))
                    output = np.vstack((output, new_time_value))
                    new_timestamp += threshold
                    current_range += threshold
#                 This is the normal row sync or if the ending lines up with the sync mark
                if current_row != end - 1 or current_range == current_row:
                    new_time_value = data[current_base:current_row, 1:].mean(0)
#                 This line checks the ending row, if it does not match with the sync mark, it will capture the rest of the values
                else:
                    new_time_value = data[current_base:, 1:].mean(0)
                temp_time = np.matrix(new_timestamp)
                new_time_value = np.hstack((temp_time, new_time_value))
                output = np.vstack((output, new_time_value))
#                 If the ending lines up with the sync mark, add the last value to the result
                if current_row == end - 1 and current_range == current_row:
                    temp_time = np.matrix(new_timestamp)
                    new_time_value = np.hstack((temp_time, data[current_row, 1:]))                 
                    output = np.vstack((output, new_time_value))
                new_timestamp += threshold
                current_range += threshold
                current_base = current_row
#        Moves back to 0 at the end of the session
        new_time_value = np.hstack((new_timestamp, np.zeros(columns - 1)))
        output = np.vstack((output, new_time_value))
        return output
    

    def replace_outliers(self, data, m=3):
        df = pd.DataFrame(data)
        sd = df.values.std()
        df[df.abs() > m * sd] = 0
        return df.values
            
    
