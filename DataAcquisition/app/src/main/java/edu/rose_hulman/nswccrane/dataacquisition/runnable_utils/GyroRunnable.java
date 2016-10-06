package edu.rose_hulman.nswccrane.dataacquisition.runnable_utils;

import datamodels.GyroDataModel;
import sqlite.MotionCollectionDBHelper;

/**
 * Created by steve on 10/3/16.
 */

public class GyroRunnable implements Runnable {
    private GyroDataModel mData;
    private MotionCollectionDBHelper mDBHelper;

    public GyroRunnable(GyroDataModel data, MotionCollectionDBHelper dbHelper) {
        mData = data;
        mDBHelper = dbHelper;
    }

    @Override
    public void run() {
        mDBHelper.insertGyroData(mData);
    }
}
