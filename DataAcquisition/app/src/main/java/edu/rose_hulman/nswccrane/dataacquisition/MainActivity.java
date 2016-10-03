package edu.rose_hulman.nswccrane.dataacquisition;

import android.app.KeyguardManager;
import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import datamodels.AccelDataModel;
import datamodels.GyroDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.interfaces.ICollectionActivity;
import sqlite.MotionCollectionDBHelper;
import sqlite.interfaces.ICollectionDBHelper;

public class MainActivity extends AppCompatActivity implements SensorEventListener, ICollectionActivity {

    private static final int MAXIMUM_LATENCY = 0;

    private static final int MAX_THREADS_TOGGLE_SERVICE = 1;

    private static final int MAX_WAIT_TIME_COLLECTION_SERVICE = 30;
    private static final int MAX_THREADS_COLLECTION_SERVICE = 10;

    private Button mCollectionButton;

    private TextView mXTextView;
    private TextView mYTextView;
    private TextView mZTextView;

    private TextView mPitchTextView;
    private TextView mRollTextView;
    private TextView mYawTextView;

    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private Sensor mGyroscope;

    private ICollectionDBHelper mCollectionDBHelper;

    private ExecutorService mToggleButtonService;
    private ExecutorService mCollectionService;

    private boolean mStarted;

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
    }

    @Override
    protected void onResume() {
        super.onResume();
        setupUIElements();
        populateSensorDependencies();
    }

    @Override
    protected void onStop() {
        super.onStop();
        teardownSensorDependencies();
    }

    private void setupUIElements() {
        mXTextView = (TextView) findViewById(R.id.x_accel_text_view);
        mYTextView = (TextView) findViewById(R.id.y_accel_text_view);
        mZTextView = (TextView) findViewById(R.id.z_accel_text_view);

        mPitchTextView = (TextView) findViewById(R.id.pitch_gyro_text_view);
        mRollTextView = (TextView) findViewById(R.id.roll_gyro_text_view);
        mYawTextView = (TextView) findViewById(R.id.yaw_gyro_text_view);

        mCollectionButton = (Button) findViewById(R.id.collection_button);
        mCollectionButton.setText(getString(R.string.collect_data));
        mCollectionButton.setOnClickListener(new CollectionClickListener());
    }

    @Override
    public void populateSensorDependencies() {
        mStarted = false;

        mToggleButtonService = Executors.newFixedThreadPool(MAX_THREADS_TOGGLE_SERVICE);
        mCollectionService = Executors.newFixedThreadPool(MAX_THREADS_COLLECTION_SERVICE);

        mCollectionDBHelper = new MotionCollectionDBHelper(this);

        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);

        mAccelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        mGyroscope = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);

        mSensorManager.registerListener(this, mAccelerometer, MAXIMUM_LATENCY);
        mSensorManager.registerListener(this, mGyroscope, MAXIMUM_LATENCY);
    }

    @Override
    public void teardownSensorDependencies() {
        mStarted = false;

        mToggleButtonService.shutdownNow();
        mCollectionService.shutdownNow();

        mSensorManager.unregisterListener(this);
    }

    private class CollectionClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            toggleCollection();
        }
    }

    @Override
    public void toggleCollection() {
        if (mStarted) {
            mCollectionButton.setActivated(false);
            mStarted = false;
            mCollectionButton.setText(R.string.collect_data);
            mToggleButtonService.execute(new ToggleButtonRunnable());
            return;
        }
        mCollectionButton.setActivated(false);
        mCollectionButton.setText(R.string.stop_collection);
        mCollectionDBHelper.setStartTime(System.currentTimeMillis());
        mStarted = true;
        mCollectionButton.setActivated(true);
    }

    @Override
    public void accelerometerChanged(AccelDataModel dataModel) {
        mCollectionService.execute(new AccelRunnable(dataModel));
        mXTextView.setText(String.format(Locale.US, getString(R.string.x_format), dataModel.getX()));
        mYTextView.setText(String.format(Locale.US, getString(R.string.y_format), dataModel.getY()));
        mZTextView.setText(String.format(Locale.US, getString(R.string.z_format), dataModel.getZ()));
    }

    @Override
    public void gyroscopeChanged(GyroDataModel dataModel) {
        mCollectionService.execute(new GyroRunnable(dataModel));
        mPitchTextView.setText(String.format(Locale.US, getString(R.string.pitch_format), dataModel.getPitch()));
        mRollTextView.setText(String.format(Locale.US, getString(R.string.roll_format), dataModel.getRoll()));
        mYawTextView.setText(String.format(Locale.US, getString(R.string.yaw_format), dataModel.getYaw()));
    }

    class ToggleButtonRunnable implements Runnable {

        public void run() {
            mCollectionService.shutdown();
            try {
                mCollectionService.awaitTermination(MAX_WAIT_TIME_COLLECTION_SERVICE, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                e.printStackTrace();
                mCollectionService.shutdownNow();
            }
            mCollectionService = Executors.newFixedThreadPool(MAX_THREADS_COLLECTION_SERVICE);
            mCollectionDBHelper.pushAccelData();
            mCollectionDBHelper.pushGyroData();
            mCollectionDBHelper.setEndTime(System.currentTimeMillis());
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    mCollectionButton.setActivated(true);
                }
            });
        }
    }

    class AccelRunnable implements Runnable {

        private AccelDataModel mData;

        public AccelRunnable(AccelDataModel data){
            mData = data;
        }

        public void run() {
            mCollectionDBHelper.insertAccelData(mData);
        }
    }

    class GyroRunnable implements Runnable {

        private GyroDataModel mData;

        public GyroRunnable(GyroDataModel data) {
            mData = data;
        }

        public void run() {
            mCollectionDBHelper.insertGyroData(mData);
        }
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (mStarted) {
            if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
                AccelDataModel dataModel = new AccelDataModel(event.timestamp, event.values[0], event.values[1], event.values[2]);
                accelerometerChanged(dataModel);
            }
            else if (event.sensor.getType() == Sensor.TYPE_GYROSCOPE) {
                GyroDataModel dataModel = new GyroDataModel(event.timestamp, event.values[0], event.values[1], event.values[2]);
                gyroscopeChanged(dataModel);
            }
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }
}