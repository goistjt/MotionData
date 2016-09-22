package edu.rose_hulman.nswccrane.dataacquisition.interfaces;

import android.util.Log;
import android.view.View;
import android.widget.Button;

import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import datamodels.AccelDataModel;
import sqlite.MotionCollectionDBHelper;

/**
 * Created by steve on 9/21/16.
 */

public interface ICollectionActivity {

    void populateSensorDependencies();

    void teardownSensorDependencies();

    void toggleCollection();

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
