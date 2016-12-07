'''
Created on Oct 31, 2016

@author: steve
'''

class MaxCollection(object): pass

GRAVITY = 9.8

class SurgeCollection(MaxCollection):
    def get_max_vel(self): return 0.8
    def get_max_neg_exc(self): return -0.307
    def get_max_pos_exc(self): return 0.408
    def get_max_accel(self): return 0.65 * GRAVITY
    def get_max_accel_diff(self): return 8.0 * GRAVITY
    class Factory:
        def create(self): return SurgeCollection()

class SwayCollection(MaxCollection):
    def get_max_vel(self): return 0.8
    def get_max_neg_exc(self): return -0.318
    def get_max_pos_exc(self): return 0.318
    def get_max_accel(self): return 0.60 * GRAVITY
    def get_max_accel_diff(self): return 8.0 * GRAVITY
    class Factory:
        def create(self): return SwayCollection()
        
class HeaveCollection(MaxCollection):
    def get_max_vel(self): return 0.6
    def get_max_neg_exc(self): return -0.240
    def get_max_pos_exc(self): return 0.261
    def get_max_accel(self): return 0.60 * GRAVITY
    def get_max_accel_diff(self): return 8.0 * GRAVITY
    class Factory:
        def create(self): return HeaveCollection()
        
class RollCollection(MaxCollection):
    def get_max_vel(self): return 40.0
    def get_max_neg_exc(self): return -16.5
    def get_max_pos_exc(self): return 16.5
    def get_max_accel(self): return 300.0
    def get_max_accel_diff(self): return 3000.0
    class Factory:
        def create(self): return RollCollection()
        
class PitchCollection(MaxCollection):
    def get_max_vel(self): return 40.0
    def get_max_neg_exc(self): return -16.5
    def get_max_pos_exc(self): return 16.5
    def get_max_accel(self): return 300.0
    def get_max_accel_diff(self): return 3000.0
    class Factory:
        def create(self): return PitchCollection()
        
class YawCollection(MaxCollection):
    def get_max_vel(self): return 50.0
    def get_max_neg_exc(self): return -20.5
    def get_max_pos_exc(self): return 20.5
    def get_max_accel(self): return 350.0
    def get_max_accel_diff(self): return 3000.0
    class Factory:
        def create(self): return YawCollection()