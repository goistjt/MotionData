'''
Created on Oct 31, 2016

@author: steve
'''

GRAVITY = 9.8

class MaxCollection(object):
    
    def __init__(self):
        self._max_vel = 0.0
        self._max_neg_exc = 0.0
        self._max_pos_exc = 0.0
        self._max_accel = 0.0
        self._max_accel_diff = 0.0
    
    def get_max_vel(self): return self._max_vel
    def get_max_neg_exc(self): return self._max_neg_exc
    def get_max_pos_exc(self): return self._max_pos_exc
    def get_max_accel(self): return self._max_accel
    def get_max_accel_diff(self): return self._max_accel_diff

class SurgeCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = 0.8
        self._max_neg_exc = -0.307
        self._max_pos_exc = 0.408
        self._max_accel = 0.65 * GRAVITY
        self._max_accel_diff = 8.0 * GRAVITY
    

class SwayCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = 0.8
        self._max_neg_exc = -0.318
        self._max_pos_exc = 0.318
        self._max_accel = 0.60 * GRAVITY
        self._max_accel_diff = 8.0 * GRAVITY
        
class HeaveCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = 0.6
        self._max_neg_exc = -0.240
        self._max_pos_exc = 0.261
        self._max_accel = 0.60 * GRAVITY
        self._max_accel_diff = 8.0 * GRAVITY
        
class RollCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = 40.0
        self._max_neg_exc = -16.5
        self._max_pos_exc = 16.5
        self._max_accel = 300.0
        self._max_accel_diff = 3000.0
        
class PitchCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = 40.0
        self._max_neg_exc = -16.5
        self._max_pos_exc = 16.5
        self._max_accel = 300.0
        self._max_accel_diff = 3000.0
        
class YawCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = 50.0
        self._max_neg_exc = -20.5
        self._max_pos_exc = 20.5
        self._max_accel = 350.0
        self._max_accel_diff = 3000.0