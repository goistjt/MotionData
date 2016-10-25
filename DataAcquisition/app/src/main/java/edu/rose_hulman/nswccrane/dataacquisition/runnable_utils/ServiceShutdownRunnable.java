package edu.rose_hulman.nswccrane.dataacquisition.runnable_utils;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import edu.rose_hulman.nswccrane.dataacquisition.MainActivity;
import edu.rose_hulman.nswccrane.dataacquisition.interfaces.ICollectionCallback;
import sqlite.MotionCollectionDBHelper;

/**
 * Created by steve on 10/3/16.
 */

public class ServiceShutdownRunnable implements Runnable {

    private static final int TIME_BEFORE_FORCEFUL_SHUTDOWN = 5;

    private ExecutorService mCollectionService;
    private MotionCollectionDBHelper mCollectionDBHelper;
    private ICollectionCallback mCallback;

    public ServiceShutdownRunnable(MainActivity activity, ExecutorService collectionService, MotionCollectionDBHelper collectionDBHelper) {
        mCollectionService = collectionService;
        mCollectionDBHelper = collectionDBHelper;
        mCallback = activity;
    }

    public void run() {
        mCollectionService.shutdown();
        try {
            mCollectionService.awaitTermination(TIME_BEFORE_FORCEFUL_SHUTDOWN, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            e.printStackTrace();
            mCollectionService.shutdownNow();
        }
        mCollectionDBHelper.pushAccelData();
        mCollectionDBHelper.pushGyroData();
        mCollectionDBHelper.setEndTime(System.nanoTime());
        mCallback.finishToggle();
    }
}
