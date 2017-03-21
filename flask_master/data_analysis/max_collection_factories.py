"""
Created on Oct 31, 2016

@author: steve
"""
# Polymorphic factory methods.

from __future__ import generators
import data_analysis.max_collections as mc

"""
This class is responsible for delivering the corresponding colleciton of maximum values (MaxCollections) based upon the
degree of freedom designation specified.
"""


class MaxCollectionFactory:
    def __init__(self):
        self.SURGE = 'surge'
        self.SWAY = 'sway'
        self.HEAVE = 'heave'
        self.ROLL = 'roll'
        self.PITCH = 'pitch'
        self.YAW = 'yaw'
        self.factories = {
            self.SURGE: mc.SurgeCollection,
            self.SWAY: mc.SwayCollection,
            self.HEAVE: mc.HeaveCollection,
            self.ROLL: mc.RollCollection,
            self.PITCH: mc.PitchCollection,
            self.YAW: mc.YawCollection
            }

    """
    Adds a collection to the dictionary with an id and a collection class.
    """
    def add_collection(self, fid, max_collection):
        self.factories.put[fid] = max_collection

    """
    Retrieves the correct class from the dictionary and instantiates an instance of it.
    """
    def create_max_collection(self, fid):
        return self.factories[fid]()
