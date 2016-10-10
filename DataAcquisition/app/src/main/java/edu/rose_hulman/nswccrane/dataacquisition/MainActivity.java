package edu.rose_hulman.nswccrane.dataacquisition;

import android.app.KeyguardManager;
import android.content.Context;
import android.content.SharedPreferences;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import butterknife.BindView;
import butterknife.ButterKnife;
import datamodels.AccelDataModel;
import datamodels.GyroDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.interfaces.ICollectionCallback;
import edu.rose_hulman.nswccrane.dataacquisition.runnable_utils.AccelRunnable;
import edu.rose_hulman.nswccrane.dataacquisition.runnable_utils.GyroRunnable;
import edu.rose_hulman.nswccrane.dataacquisition.runnable_utils.ServiceShutdownRunnable;
import sqlite.MotionCollectionDBHelper;
import edu.rose_hulman.nswccrane.dataacquisition.fragments.ExportDialog;

public class MainActivity extends AppCompatActivity implements SensorEventListener, View.OnClickListener, ICollectionCallback {

    @BindView(R.id.collection_button)
    public Button mCollectionButton;

    @BindView(R.id.x_accel_text_view)
    public TextView mXTextView;

    @BindView(R.id.y_accel_text_view)
    public TextView mYTextView;

    @BindView(R.id.z_accel_text_view)
    public TextView mZTextView;

    @BindView(R.id.pitch_gyro_text_view)
    public TextView mPitchTextView;

    @BindView(R.id.roll_gyro_text_view)
    public TextView mRollTextView;

    @BindView(R.id.yaw_gyro_text_view)
    public TextView mYawTextView;

    @BindView(R.id.calibration_button)
    Button mCalibrationButton;

    @BindView(R.id.export_button)
    Button mExportButton;

    private double max_x_noise;
    private double max_y_noise;
    private double max_z_noise;

    private double max_roll_noise;
    private double max_pitch_noise;
    private double max_yaw_noise;

    private AccelDataModel mPrevAccelModel;
    private GyroDataModel mPrevGyroModel;

    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private Sensor mGyroscope;

    private MotionCollectionDBHelper mCollectionDBHelper;

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
        ButterKnife.bind(this);
        this.mCalibrationButton.setOnClickListener(this);
        this.mExportButton.setOnClickListener(this);
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.calibration_button:
                openCalibrationDialog();
                break;
            case R.id.export_button:
                openExportDialog();
                break;
            case R.id.collection_button:
                if (mStarted) {
                    collectionOff();
                }
                else {
                    collectionOn();
                }
            default:
                //Empty
        }
    }

    private void openExportDialog() {
        ExportDialog exportDialog = new ExportDialog();
        exportDialog.show(getFragmentManager(), "export_redirect");
    }

    private void openCalibrationDialog() {
        AlertDialog.Builder dialog = new AlertDialog.Builder(this);
        dialog.setTitle(R.string.calibration_dialog_title);
        dialog.setMessage(R.string.please_secure_device);
        dialog.setPositiveButton(R.string.calibrate, new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                Intent startCalibrationIntent = new Intent(MainActivity.this, CalibrationActivity.class);
                startActivity(startCalibrationIntent);
            }
        });
        dialog.setNegativeButton(R.string.cancel, new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                dialog.dismiss();
            }
        });
        dialog.show();
    }

    @Override
    protected void onResume() {
        super.onResume();
        populatePreservedValues();
        setupUIElements();
        initializeCollectionDependencies();
    }


    private void populatePreservedValues() {
        SharedPreferences sharedPref = this.getSharedPreferences(getString(R.string.calibration_prefs), 0);
        max_x_noise = sharedPref.getFloat(getString(R.string.x_threshold), getResources().getInteger(R.integer.DEFAULT_X_THRESHOLD));
        max_y_noise = sharedPref.getFloat(getString(R.string.y_threshold), getResources().getInteger(R.integer.DEFAULT_Y_THRESHOLD));
        max_z_noise = sharedPref.getFloat(getString(R.string.z_threshold), getResources().getInteger(R.integer.DEFAULT_Z_THRESHOLD));
        max_pitch_noise = sharedPref.getFloat(getString(R.string.pitch_threshold), getResources().getInteger(R.integer.DEFAULT_PITCH_THRESHOLD));
        max_roll_noise = sharedPref.getFloat(getString(R.string.roll_threshold), getResources().getInteger(R.integer.DEFAULT_ROLL_THRESHOLD));
        max_yaw_noise = sharedPref.getFloat(getString(R.string.yaw_threshold), getResources().getInteger(R.integer.DEFAULT_YAW_THRESHOLD));
    }

    @Override
    protected void onStop() {
        super.onStop();
        teardownCollectionDependencies();
    }

    private void setupUIElements() {
        mCollectionButton.setOnClickListener(this);
        mCalibrationButton.setOnClickListener(this);
    }

    public void initializeCollectionDependencies() {
        mStarted = false;

        mToggleButtonService = Executors.newFixedThreadPool(getResources().getInteger(R.integer.DEFAULT_TOGGLE_THREADS));
        mCollectionService = Executors.newFixedThreadPool(getResources().getInteger(R.integer.DEFAULT_COLLECTION_THREADS));

        mCollectionDBHelper = new MotionCollectionDBHelper(this);

        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        mAccelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        mGyroscope = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
    }

    public void teardownCollectionDependencies() {
        mStarted = false;

        mToggleButtonService.shutdownNow();
        mCollectionService.shutdownNow();

        mSensorManager.unregisterListener(this);
    }

    public void collectionOff() {
        mCollectionButton.setActivated(false);
        mStarted = false;
        mCollectionDBHelper.setEndTime(System.currentTimeMillis());
        mCollectionButton.setText(R.string.collect_data);
        mSensorManager.unregisterListener(this);
        mToggleButtonService.execute(new ServiceShutdownRunnable(this, mCollectionService, mCollectionDBHelper));
    }

    public void collectionOn() {
        mCollectionButton.setActivated(false);
        if (mAccelerometer != null) {
            mSensorManager.registerListener(this, mAccelerometer, getResources().getInteger(R.integer.DEFAULT_COLLECTION_LATENCY));
        }
        if (mGyroscope != null) {
            mSensorManager.registerListener(this, mGyroscope, getResources().getInteger(R.integer.DEFAULT_COLLECTION_LATENCY));
        }
        mCollectionButton.setText(R.string.stop_collection);
        mCollectionDBHelper.setStartTime(System.currentTimeMillis());
        mStarted = true;
        mCollectionButton.setActivated(true);
    }

    public void accelerometerChanged(AccelDataModel dataModel) {
        if (this.mPrevAccelModel == null) {
            this.mPrevAccelModel = dataModel;
        }
        else {
            if (Math.abs(this.mPrevAccelModel.getX() - dataModel.getX()) < this.max_x_noise) {
                dataModel.setX(this.mPrevAccelModel.getX());
            }
            if (Math.abs(this.mPrevAccelModel.getY() - dataModel.getY()) < this.max_y_noise) {
                dataModel.setY(this.mPrevAccelModel.getY());
            }
            if (Math.abs(this.mPrevAccelModel.getZ() - dataModel.getZ()) < this.max_z_noise) {
                dataModel.setZ(this.mPrevAccelModel.getZ());
            }
        }
        this.mPrevAccelModel = dataModel;
        mCollectionService.execute(new AccelRunnable(dataModel, mCollectionDBHelper));
        mXTextView.setText(String.format(Locale.US, getString(R.string.x_format), dataModel.getX()));
        mYTextView.setText(String.format(Locale.US, getString(R.string.y_format), dataModel.getY()));
        mZTextView.setText(String.format(Locale.US, getString(R.string.z_format), dataModel.getZ()));
    }

    public void gyroscopeChanged(GyroDataModel dataModel) {
        if (this.mPrevGyroModel == null) {
            this.mPrevGyroModel = dataModel;
        }
        else {
            if (Math.abs(this.mPrevGyroModel.getPitch() - dataModel.getPitch()) < this.max_pitch_noise) {
                dataModel.setPitch(this.mPrevGyroModel.getPitch());
            }
            if (Math.abs(this.mPrevGyroModel.getRoll() - dataModel.getRoll()) < this.max_roll_noise) {
                dataModel.setRoll(this.mPrevGyroModel.getRoll());
            }
            if (Math.abs(this.mPrevGyroModel.getYaw() - dataModel.getYaw()) < this.max_yaw_noise) {
                dataModel.setYaw(this.mPrevGyroModel.getYaw());
            }
        }
        this.mPrevGyroModel = dataModel;
        mCollectionService.execute(new GyroRunnable(dataModel, mCollectionDBHelper));
        mPitchTextView.setText(String.format(Locale.US, getString(R.string.pitch_format), dataModel.getPitch()));
        mRollTextView.setText(String.format(Locale.US, getString(R.string.roll_format), dataModel.getRoll()));
        mYawTextView.setText(String.format(Locale.US, getString(R.string.yaw_format), dataModel.getYaw()));
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        switch (event.sensor.getType()) {
            case Sensor.TYPE_ACCELEROMETER:
                AccelDataModel accelModel = new AccelDataModel(event.timestamp, event.values[0], event.values[1], event.values[2]);
                accelerometerChanged(accelModel);
                break;
            case Sensor.TYPE_GYROSCOPE:
                GyroDataModel gyroModel = new GyroDataModel(event.timestamp, event.values[0], event.values[1], event.values[2]);
                gyroscopeChanged(gyroModel);
            default:
                //Empty
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }

    @Override
    public void finishToggle() {
        mCollectionService = Executors.newFixedThreadPool(getResources().getInteger(R.integer.DEFAULT_COLLECTION_THREADS));
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                mCollectionButton.setActivated(true);
            }
        });
    }
}