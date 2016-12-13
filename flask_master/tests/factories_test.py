'''
Created on Dec 11, 2016

@author: TrottaSN
'''
import unittest

from data_analysis import max_collection_factories as mcf, max_collections as mc

class Test(unittest.TestCase):


    def setUp(self):
        self.mcfactory = mcf.MaxCollectionFactory()


    def tearDown(self):
        self.mcfactory = None

    def testGetSurgeCollection(self):
        surgeCollection = self.mcfactory.createMaxCollection(self.mcfactory.SURGE)
        self.assertIs(type(surgeCollection), mc.SurgeCollection)
        
    def testGetSwayCollection(self):
        swayCollection = self.mcfactory.createMaxCollection(self.mcfactory.SWAY)
        self.assertIs(type(swayCollection), mc.SwayCollection)
    
    def testGetHeaveCollection(self):
        heaveCollection = self.mcfactory.createMaxCollection(self.mcfactory.HEAVE)
        self.assertIs(type(heaveCollection), mc.HeaveCollection)
    
    def testGetRollCollection(self):
        rollCollection = self.mcfactory.createMaxCollection(self.mcfactory.ROLL)
        self.assertIs(type(rollCollection), mc.RollCollection)
        
    def testGetPitchCollection(self):
        pitchCollection = self.mcfactory.createMaxCollection(self.mcfactory.PITCH)
        self.assertIs(type(pitchCollection), mc.PitchCollection)
        
    def testGetYawCollection(self):
        yawCollection = self.mcfactory.createMaxCollection(self.mcfactory.YAW)
        self.assertIs(type(yawCollection), mc.YawCollection)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetSurgeCollection']
    unittest.main()