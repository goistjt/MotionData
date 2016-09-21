package edu.rose_hulman.nswccrane.dataacquisition.interfaces;

import datamodels.AccelDataModel;
import sqlite.MotionCollectionDBHelper;

/**
 * Created by steve on 9/21/16.
 */

public interface ICollectionActivity {

    void populateSensorDependencies();

    void teardownSensorDependencies();

    void collectionButtonSetup();

    class InsertionThread implements Runnable {

        private AccelDataModel mData;
        private MotionCollectionDBHelper mMotionCollectionDBHelper;

        public InsertionThread(AccelDataModel dataModel, MotionCollectionDBHelper motionCollectionDBHelper) {
            mData = dataModel;
            mMotionCollectionDBHelper = motionCollectionDBHelper;
        }

        public void run() {
            mMotionCollectionDBHelper.InsertModelIntoDB(mData);
        }
    }
}
