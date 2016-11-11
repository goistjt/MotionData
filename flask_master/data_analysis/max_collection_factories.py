'''
Created on Oct 31, 2016

@author: steve
'''
# Polymorphic factory methods.

from __future__ import generators

class MaxCollectionFactory:
    factories = {}
    
    def addFactory(fid, maxCollectionFactory):
        MaxCollectionFactory.factories.put[fid] = maxCollectionFactory
        
    addFactory = staticmethod(addFactory)
    
    def createMaxCollection(fid):
        if not MaxCollectionFactory.factories.has_key(fid):
            MaxCollectionFactory.factories[fid] = eval(fid + '.Factory()')
        return MaxCollectionFactory.factories[fid].create()
    
    createMaxCollection = staticmethod(createMaxCollection)