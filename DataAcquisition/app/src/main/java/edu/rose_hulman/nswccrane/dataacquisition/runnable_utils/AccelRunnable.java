package edu.rose_hulman.nswccrane.dataacquisition.runnable_utils;

import datamodels.AccelDataModel;
import sqlite.MotionCollectionDBHelper;

/**
 * Created by steve on 10/3/16.
 */

public class AccelRunnable implements Runnable {

    private AccelDataModel mData;
    private MotionCollectionDBHelper mDBHelper;

    public AccelRunnable(AccelDataModel data, MotionCollectionDBHelper dbHelper) {
        mData = data;
        mDBHelper = dbHelper;
    }

    public void run() {
        mDBHelper.insertAccelData(mData);
    }
}
