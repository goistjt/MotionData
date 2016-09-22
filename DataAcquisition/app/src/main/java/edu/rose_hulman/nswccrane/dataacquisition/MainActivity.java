package edu.rose_hulman.nswccrane.dataacquisition;

import android.app.KeyguardManager;
import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;

import datamodels.AccelDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.interfaces.ICollectionActivity;
import sqlite.MotionCollectionDBHelper;

public class MainActivity extends AppCompatActivity implements SensorEventListener, ICollectionActivity {

    private Button mCollectionButton;
    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private MotionCollectionDBHelper mMotionCollectionDBHelper;
    private ExecutorService mInsertionThreadPool;
    private boolean mStarted = false;
    private long SECONDS_TO_INSERTION_AWAIT_TIMEOUT = 30;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (BuildConfig.DEBUG) {
            KeyguardManager km = (KeyguardManager) getSystemService(Context.KEYGUARD_SERVICE);
            KeyguardManager.KeyguardLock keyguardLock = km.newKeyguardLock("TAG");
            keyguardLock.disableKeyguard();
            getWindow().addFlags(WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON);
        }
        setContentView(R.layout.activity_main);
        mCollectionButton = (Button) findViewById(R.id.collection_button);
        mMotionCollectionDBHelper = new MotionCollectionDBHelper(this, new Semaphore(1));
        mInsertionThreadPool = Executors.newFixedThreadPool(10);
        mCollectionButton.setOnClickListener(new CollectionClickListener());
    }

    public void populateSensorDependencies() {
        if (mSensorManager == null) {
            mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        }
        if (mAccelerometer == null) {
            mAccelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        }
        if (!mStarted){
            mSensorManager.registerListener(this, mAccelerometer, SensorManager.SENSOR_DELAY_FASTEST);
            mStarted = true;
        }
    }

    public void teardownSensorDependencies() {
        if (mStarted) {
            mSensorManager.unregisterListener(this);
            mStarted = false;
        }
        mAccelerometer = null;
        mSensorManager = null;
        mMotionCollectionDBHelper = null;
    }

    private class CollectionClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            // May want to make this a thread in and of itself. Investigate whether onClick starts asynchronously.
            toggleCollection();
        }
    }

    public void toggleCollection() {
        if(mStarted) {
            mCollectionButton.setActivated(false);
            mInsertionThreadPool.shutdown();
            try {
                mInsertionThreadPool.awaitTermination(SECONDS_TO_INSERTION_AWAIT_TIMEOUT, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                Log.e("INT_AWAIT", e.getMessage());
                mInsertionThreadPool.shutdownNow();
            }
            mCollectionButton.setText("Start Collection");
            mMotionCollectionDBHelper.DeleteCurrentAccelData();
            mStarted = false;
            mCollectionButton.setActivated(true);
            return;
        }
        mCollectionButton.setActivated(false);
        mInsertionThreadPool = Executors.newFixedThreadPool(10);
        mCollectionButton.setText("Stop Collection and Delete Current Data");
        mStarted = true;
        mCollectionButton.setActivated(true);
    }

    @Override
    protected void onStart() {
        super.onStart();
        populateSensorDependencies();
    }

    @Override
    protected void onResume() {
        super.onResume();
        populateSensorDependencies();
    }

    protected void onPause() {
        super.onPause();
        teardownSensorDependencies();
    }

    protected void onStop() {
        super.onStop();
        teardownSensorDependencies();
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (mStarted) {
            final AccelDataModel accelData = new AccelDataModel(System.currentTimeMillis(), event.values[0], event.values[1], event.values[2]);
            mInsertionThreadPool.submit(new ICollectionActivity.InsertionThread(accelData, mMotionCollectionDBHelper));
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }
}