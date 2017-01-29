"""
Created on Dec 11, 2016

@author: TrottaSN
"""
import unittest

from data_analysis import max_collection_factories as mcf, max_collections as mc


class Test(unittest.TestCase):
    def setUp(self):
        self.mcfactory = mcf.MaxCollectionFactory()

    def tearDown(self):
        self.mcfactory = None

    def testGetSurgeCollection(self):
        surge_collection = self.mcfactory.create_max_collection(self.mcfactory.SURGE)
        self.assertIs(type(surge_collection), mc.SurgeCollection)

    def testGetSwayCollection(self):
        sway_collection = self.mcfactory.create_max_collection(self.mcfactory.SWAY)
        self.assertIs(type(sway_collection), mc.SwayCollection)

    def testGetHeaveCollection(self):
        heave_collection = self.mcfactory.create_max_collection(self.mcfactory.HEAVE)
        self.assertIs(type(heave_collection), mc.HeaveCollection)

    def testGetRollCollection(self):
        roll_collection = self.mcfactory.create_max_collection(self.mcfactory.ROLL)
        self.assertIs(type(roll_collection), mc.RollCollection)

    def testGetPitchCollection(self):
        pitch_collection = self.mcfactory.create_max_collection(self.mcfactory.PITCH)
        self.assertIs(type(pitch_collection), mc.PitchCollection)

    def testGetYawCollection(self):
        yaw_collection = self.mcfactory.create_max_collection(self.mcfactory.YAW)
        self.assertIs(type(yaw_collection), mc.YawCollection)


if __name__ == "__main__":
    unittest.main()
