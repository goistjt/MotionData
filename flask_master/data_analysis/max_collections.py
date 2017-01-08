'''
Created on Oct 31, 2016

@author: steve
'''

import decimal as dc

GRAVITY = 9.8

class MaxCollection(object):
    
    def __init__(self):
        self._max_vel = dc.Decimal(0.0)
        self._max_neg_exc = dc.Decimal(0.0)
        self._max_pos_exc = dc.Decimal(0.0)
        self._max_accel = dc.Decimal(0.0)
        self._max_accel_diff = dc.Decimal(0.0)
    
    def get_max_vel(self): return self._max_vel
    def get_max_neg_exc(self): return self._max_neg_exc
    def get_max_pos_exc(self): return self._max_pos_exc
    def get_max_accel(self): return self._max_accel
    def get_max_accel_diff(self): return self._max_accel_diff

class SurgeCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = dc.Decimal(0.8)
        self._max_neg_exc = dc.Decimal(-0.307)
        self._max_pos_exc = dc.Decimal(0.408)
        self._max_accel = dc.Decimal(0.65) * dc.Decimal(GRAVITY)
        self._max_accel_diff = dc.Decimal(8.0) * dc.Decimal(GRAVITY)
    

class SwayCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = dc.Decimal(0.8)
        self._max_neg_exc = dc.Decimal(-0.318)
        self._max_pos_exc = dc.Decimal(0.318)
        self._max_accel = dc.Decimal(0.60) * dc.Decimal(GRAVITY)
        self._max_accel_diff = dc.Decimal(8.0) * dc.Decimal(GRAVITY)
        
class HeaveCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = dc.Decimal(0.6)
        self._max_neg_exc = dc.Decimal(-0.240)
        self._max_pos_exc = dc.Decimal(0.261)
        self._max_accel = dc.Decimal(0.60) * dc.Decimal(GRAVITY)
        self._max_accel_diff = dc.Decimal(8.0) * dc.Decimal(GRAVITY)
        
class RollCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = dc.Decimal(40.0)
        self._max_neg_exc = dc.Decimal(-16.5)
        self._max_pos_exc = dc.Decimal(16.5)
        self._max_accel = dc.Decimal(300.0)
        self._max_accel_diff = dc.Decimal(3000.0)
        
class PitchCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = dc.Decimal(40.0)
        self._max_neg_exc = dc.Decimal(-16.5)
        self._max_pos_exc = dc.Decimal(16.5)
        self._max_accel = dc.Decimal(300.0)
        self._max_accel_diff = dc.Decimal(3000.0)
        
class YawCollection(MaxCollection):
    
    def __init__(self):
        self._max_vel = dc.Decimal(50.0)
        self._max_neg_exc = dc.Decimal(-20.5)
        self._max_pos_exc = dc.Decimal(20.5)
        self._max_accel = dc.Decimal(350.0)
        self._max_accel_diff = dc.Decimal(3000.0)