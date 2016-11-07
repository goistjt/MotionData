'''
Created on Oct 31, 2016

@author: steve
'''
# Polymorphic factory methods.

from __future__ import generators
import flask_master.data_analysis.max_collections as mc

class MaxCollectionFactory:
    factories = {}
    
    def addFactory(fid, maxCollectionFactory):
        MaxCollectionFactory.factories.put[fid] = maxCollectionFactory
        
    addFactory = staticmethod(addFactory)
    addFactory(0, mc.SurgeCollection)
    addFactory(1, mc.SwayCollection)
    addFactory(2, mc.HeaveCollection)
    addFactory(3, mc.RollCollection)
    addFactory(4, mc.PitchCollection)
    addFactory(5, mc.YawCollection)
    
    def createMaxCollection(fid):
        if not MaxCollectionFactory.factories.has_key(fid):
            MaxCollectionFactory.factories[fid] = eval(fid + '.Factory()')
        return MaxCollectionFactory.factories[fid].create()
    
    createMaxCollection = staticmethod(createMaxCollection)