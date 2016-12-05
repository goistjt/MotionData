'''
Created on Oct 31, 2016

@author: yangr
'''
from _random import Random
import pandas as pd
import numpy as np

class DiscreteScaling(object):
    '''
    classdocs
    '''
    def __init__(self, resolution = 1000):
        '''
        Constructor
        '''
        self.resolution = resolution
    
    def getRecords(self, session, record_id):
        return Random.random()    