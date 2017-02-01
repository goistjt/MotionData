'''
Created on Jan 18, 2017

@author: yangr
'''
import numpy as np
import pandas as pd

class discrete_analysis():
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
        for row_num in range(total_row-1):
        #skipping the first and last row since the machine starts at 0 and ends at 0
            if row_num == 0:
                continue
            if row_num > accel_processed and self.is_empty_record(self.accel_s, self.accel_e, data[row_num:]):
                (accel_processed, data) = self.average_Neighbors(row_num, data)
            if row_num > gyro_processed and self.is_empty_record(self.gyro_s, self.gyro_e, data[row_num:]):
                (gyro_processed, data) = self.average_Neighbors(row_num, data)
        return data

    def is_empty_record(self, s_col, e_col, array):
        return np.all(array[s_col:e_col]==0)
    
    # This starts the average neighboring process, 
    # and find the next point that has a value
    def average_Neighbors(self, row_num, s_col, e_col, data):
        cur = row_num
        while self.is_empty_record(self.accel_s, self.accel_e, data[cur:]):
            cur = cur + 1
        if cur+1 == data.shape[0]:
            data = self.fill_forward_in_time(row_num, cur, s_col, e_col, data)
        elif row_num == 0:
            data = self.fill_back_in_time(row_num, cur, s_col, e_col, data)
        else:
            data = self.fill_inbetween_time(row_num, cur, s_col, e_col, data)
        return (cur+1, data)
    
    def fill_forward_in_time(self, s_t, e_t, s_col, e_col, data):
        time_interval = e_t - s_t + 1
        # Form an array of changes
        change = np.squeeze(np.asarray((data[s_t-1,s_col:e_col] / time_interval)))
        for row in range(s_t , e_t+1):
            data[row, s_col:e_col] = np.subtract(data[row-1, s_col:e_col], change)
        return data
    
#     Starting time is the first empty cell, ending time is the first cell contains data
    def fill_back_in_time(self, s_t, e_t, s_col, e_col, data):
        time_interval = e_t - s_t + 1
        change = np.squeeze(np.asarray((data[e_t,s_col:e_col] / time_interval)))
        for row in range(e_t-1, s_t-1, -1):
            data[row, s_col:e_col] = np.subtract(data[row+1, s_col:e_col], change)
        return data
    
    def fill_inbetween_time(self, s_t, e_t, s_col, e_col, data):
        time_interval = e_t - s_t 
        change = np.squeeze(np.asarray(np.subtract(data[e_t,s_col:e_col], data[s_t, s_col:e_col]))) / time_interval
        for row in range(s_t+1, e_t):
            data[row, s_col:e_col] = np.add(data[row-1, s_col:e_col], change)
        return data
    
    def sync_thresholds(self, data ,threshold = 0.4):
        output = np.zeros(7)
        shrinked_row, current, end = 1, 0, data.shape(0)
        while current < end:
            rows_within_thresholds = 0
            current_range = data[current][0] + threshold
            valid_accel_rows, valid_gyro_rows = np.array([]),np.array([])
            
            while data[current+rows_within_thresholds][0] < current_range:
                rows_within_thresholds = rows_within_thresholds + 1
                is_empty_left = self.is_empty_record(self.accel_s, self.accel_e, data[current+rows_within_thresholds, :])
                is_empty_right = self.is_empty_record(self.gyro_s, self.gyro_e, data[current+rows_within_thresholds, :])
                if is_empty_left:
                    valid_accel_rows = np.vstack((valid_accel_rows, data[current+rows_within_thresholds, self.accel_s:self.accel_e]))
                if is_empty_right:
                    valid_gyro_rows = np.vstack((valid_gyro_rows, data[current+rows_within_thresholds, self.gyro_s:self.gyro_e]))
            current = current + rows_within_thresholds
            
            if valid_accel_rows.shape[0] == 0:
                valid_accel_rows = np.zeros(3)
            if valid_gyro_rows.shape[0] == 0:
                valid_gyro_rows = np.zeros(3)
            
            cur_row = np.hstack(shrinked_row*threshold, current(valid_accel_rows.mean(), valid_gyro_rows.mean()))
            output = np.vstack(output,  cur_row)
            shrinked_row = shrinked_row+1
            
    def replace_outliers(self, data, m=3):
        df = pd.DataFrame(data)
        sd = df.values.std()
        df[df.abs()>m*sd] = 0
        return df.values
            
    