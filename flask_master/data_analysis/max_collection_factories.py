"""
Created on Oct 31, 2016

@author: steve
"""
# Polymorphic factory methods.

from __future__ import generators
import data_analysis.max_collections as mc


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

    def add_collection(self, fid, max_collection):
        self.factories.put[fid] = max_collection

    def create_max_collection(self, fid):
        return self.factories[fid]()
