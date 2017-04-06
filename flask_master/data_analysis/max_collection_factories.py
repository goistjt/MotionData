"""
Created on Oct 31, 2016

@author: steve
"""
# Polymorphic factory methods.

from __future__ import generators
import data_analysis.max_collections as mc


class MaxCollectionFactory:
    """
    This class is responsible for delivering the corresponding colleciton of maximum values (MaxCollections) based upon the
    degree of freedom designation specified.
    """

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
        """
        Adds a collection to the dictionary with an id and a collection class.

        :param: fid - the identifier for the input collection object
                max_collection - the MaxCollection object to be stored in the dictionary

        :returns: None

        """

        self.factories.put[fid] = max_collection

    def create_max_collection(self, fid):
        """
        Retrieves the correct class from the dictionary and instantiates an instance of it.

        :param: fid - the identifier for the object to retrieve

        :returns: MaxCollection object desired with that fid or None if not found from fid input

        """

        return self.factories[fid]()
