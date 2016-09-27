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
import edu.rose_hulman.nswccrane.dataacquisition.interfaces.ICollectionCallback;
import sqlite.MotionCollectionDBHelper;
import sqlite.interfaces.ICollectionDBHelper;

public class MainActivity extends AppCompatActivity implements SensorEventListener, ICollectionActivity, ICollectionCallback {

    private static final int MAXIMUM_LATENCY = 0;

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
        populateSensorDependencies();
    }

    @Override
    protected void onStop() {
        super.onStop();
        teardownSensorDependencies();
    }

    @Override
    public void populateSensorDependencies() {
        mXTextView = (TextView) findViewById(R.id.x_accel_text_view);
        mYTextView = (TextView) findViewById(R.id.y_accel_text_view);
        mZTextView = (TextView) findViewById(R.id.z_accel_text_view);
        mPitchTextView = (TextView) findViewById(R.id.pitch_gyro_text_view);
        mRollTextView = (TextView) findViewById(R.id.roll_gyro_text_view);
        mYawTextView = (TextView) findViewById(R.id.yaw_gyro_text_view);
        mToggleButtonService = Executors.newFixedThreadPool(1);
        mCollectionService = Executors.newFixedThreadPool(Integer.MAX_VALUE);
        mCollectionButton = (Button) findViewById(R.id.collection_button);
        mCollectionButton.setOnClickListener(new CollectionClickListener());
        mCollectionDBHelper = new MotionCollectionDBHelper(this);
        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        mAccelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        mGyroscope = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        mSensorManager.registerListener(this, mAccelerometer, MAXIMUM_LATENCY);
        mSensorManager.registerListener(this, mGyroscope, MAXIMUM_LATENCY);
        mStarted = false;
    }

    @Override
    public void teardownSensorDependencies() {
        mToggleButtonService.shutdown();
        try {
            mToggleButtonService.awaitTermination(30, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            mToggleButtonService.shutdown();
            e.printStackTrace();
        }
        mCollectionService.shutdown();
        try {
            mCollectionService.awaitTermination(30, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            e.printStackTrace();
            mCollectionService.shutdownNow();
        }
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
            mCollectionButton.setText(R.string.StartCollection);
            mToggleButtonService.execute(new PushRunnable(this));
            mStarted = false;
            return;
        }
        mCollectionButton.setActivated(false);
        mCollectionButton.setText(R.string.StopCollection);
        mStarted = true;
        mCollectionButton.setActivated(true);
    }

    @Override
    public void resetCollectionButton() {
        mCollectionButton.setActivated(true);
    }

    @Override
    public void setAccelTextViews(double x, double y, double z) {
        mXTextView.setText(String.format(Locale.US, getString(R.string.XFormat), x));
        mYTextView.setText(String.format(Locale.US, getString(R.string.YFormat), y));
        mZTextView.setText(String.format(Locale.US, getString(R.string.ZFormat), z));
    }

    @Override
    public void setGyroTextViews(double pitch, double roll, double yaw) {
        mPitchTextView.setText(String.format(Locale.US, getString(R.string.PitchFormat), pitch));
        mRollTextView.setText(String.format(Locale.US, getString(R.string.RollFormat), roll));
        mYawTextView.setText(String.format(Locale.US, getString(R.string.YawFormat), yaw));
    }

    class PushRunnable implements Runnable {

        private ICollectionCallback mCallback;

        public PushRunnable(ICollectionCallback callback) {
            mCallback = callback;
        }

        public void run() {
            mCollectionDBHelper.pushAccelData();
            mCollectionDBHelper.pushGyroData();
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    mCallback.resetCollectionButton();
                }
            });
        }
    }

    class AccelRunnable implements Runnable {

        private AccelDataModel mData;
        private ICollectionCallback mCallback;

        public AccelRunnable(AccelDataModel data, ICollectionCallback callback){
            mData = data;
            mCallback = callback;
        }

        public void run() {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    mCallback.setAccelTextViews(mData.getX(), mData.getY(), mData.getZ());
                }
            });
            mCollectionDBHelper.insertAccelData(mData);
        }
    }

    class GyroRunnable implements Runnable {

        private GyroDataModel mData;
        private ICollectionCallback mCallback;

        public GyroRunnable(GyroDataModel data, ICollectionCallback callback) {
            mData = data;
            mCallback = callback;
        }

        public void run() {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    mCallback.setGyroTextViews(mData.getPitch(), mData.getRoll(), mData.getYaw());
                }
            });
            mCollectionDBHelper.insertGyroData(mData);
        }
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (mStarted) {
            if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
                mCollectionService.execute(new AccelRunnable(new AccelDataModel(event.timestamp, event.values[0], event.values[1], event.values[2]), this));
            }
            else if (event.sensor.getType() == Sensor.TYPE_GYROSCOPE) {
                mCollectionService.execute(new GyroRunnable(new GyroDataModel(event.timestamp, event.values[0], event.values[1], event.values[2]), this));
            }
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }
}