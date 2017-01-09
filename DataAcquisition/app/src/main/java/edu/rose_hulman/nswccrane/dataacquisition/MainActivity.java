package edu.rose_hulman.nswccrane.dataacquisition;

import android.app.KeyguardManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.os.Handler;
import android.support.annotation.IntegerRes;
import android.support.v7.app.AppCompatActivity;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import butterknife.BindView;
import butterknife.ButterKnife;
import datamodels.AccelDataModel;
import datamodels.GyroDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.fragments.CalibrationDialog;
import edu.rose_hulman.nswccrane.dataacquisition.fragments.ExportDialog;
import edu.rose_hulman.nswccrane.dataacquisition.interfaces.ICollectionCallback;
import edu.rose_hulman.nswccrane.dataacquisition.runnable_utils.AccelRunnable;
import edu.rose_hulman.nswccrane.dataacquisition.runnable_utils.GyroRunnable;
import edu.rose_hulman.nswccrane.dataacquisition.runnable_utils.ServiceShutdownRunnable;
import sqlite.MotionCollectionDBHelper;

import static edu.rose_hulman.nswccrane.dataacquisition.SettingsActivity.SETTINGS_RATE;

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

    @BindView(R.id.record_time_edit)
    EditText mRecordTimeEdit;

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

    private int pollRate;
    public static final int MS_TO_US = 1000;
    private float yawOffset;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        KeyguardManager km = (KeyguardManager) getSystemService(Context.KEYGUARD_SERVICE);
        KeyguardManager.KeyguardLock keyguardLock = km.newKeyguardLock("TAG");
        keyguardLock.disableKeyguard();
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON);
        setContentView(R.layout.activity_main);
        ButterKnife.bind(this);
        SharedPreferences settings = getApplicationContext().getSharedPreferences("Settings", 0);
        pollRate = settings.getInt(SETTINGS_RATE, 40);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.main_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.settings:
                startActivity(new Intent(this, SettingsActivity.class));
                break;
            default:
                //No other cases
        }
        return super.onOptionsItemSelected(item);
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
                    mCollectionButton.setEnabled(false);
                    collectionOff();
                } else {
                    handleRecordingTimer();
                }
            default:
                //Empty
        }
    }

    private void handleRecordingTimer() {
        mCollectionButton.setEnabled(false);
        collectionOn();
        yawOffset = getSharedPreferences(getString(R.string.calibration_prefs), 0).getFloat("yaw_offset", 0f);
        if (!mRecordTimeEdit.getText().toString().isEmpty() && Integer.parseInt(mRecordTimeEdit.getText().toString()) != 0) {

            Runnable runnable = new Runnable() {
                @Override
                public void run() {
                    if (mStarted) {
                        mCollectionButton.setEnabled(false);
                        collectionOff();
                    }
                }
            };
            Handler handler = new Handler();
            handler.postDelayed(runnable, Integer.parseInt(mRecordTimeEdit.getText().toString()) * 60 * 1000);

        }
    }

    private void openExportDialog() {
        ExportDialog exportDialog = new ExportDialog();
        exportDialog.setActivity(this);
        exportDialog.show(getFragmentManager(), ExportDialog.TAG);
    }

    private void openCalibrationDialog() {
        CalibrationDialog calibrationDialog = new CalibrationDialog();
        calibrationDialog.show(getFragmentManager(), CalibrationDialog.TAG);
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
        SharedPreferences settings = getApplicationContext().getSharedPreferences(getString(R.string.calibration_prefs), 0);
        SharedPreferences.Editor editor = settings.edit();
        editor.putFloat(getString(R.string.x_threshold), getResources().getInteger(R.integer.DEFAULT_X_THRESHOLD));
        editor.putFloat(getString(R.string.y_threshold), getResources().getInteger(R.integer.DEFAULT_Y_THRESHOLD));
        editor.putFloat(getString(R.string.z_threshold), getResources().getInteger(R.integer.DEFAULT_Z_THRESHOLD));
        editor.putFloat(getString(R.string.roll_threshold), getResources().getInteger(R.integer.DEFAULT_PITCH_THRESHOLD));
        editor.putFloat(getString(R.string.pitch_threshold), getResources().getInteger(R.integer.DEFAULT_ROLL_THRESHOLD));
        editor.putFloat(getString(R.string.yaw_threshold), getResources().getInteger(R.integer.DEFAULT_YAW_THRESHOLD));
        editor.apply();
    }

    private void setupUIElements() {
        mCollectionButton.setOnClickListener(this);
        mCalibrationButton.setOnClickListener(this);
        mExportButton.setOnClickListener(this);
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
        mStarted = false;
        mCollectionButton.setText(R.string.collect_data);
        mSensorManager.unregisterListener(this);
        mToggleButtonService.execute(new ServiceShutdownRunnable(this, mCollectionService, mCollectionDBHelper));
    }

    public void collectionOn() {
        mCollectionDBHelper.setStartTime(System.currentTimeMillis());
        if (mAccelerometer != null) {
            mSensorManager.registerListener(this, mAccelerometer, pollRate * MS_TO_US);
        }
        if (mGyroscope != null) {
            mSensorManager.registerListener(this, mGyroscope, pollRate * MS_TO_US);
        }
        mCollectionButton.setText(R.string.stop_collection);
        mStarted = true;
        mCollectionButton.setEnabled(true);
    }

    public void accelerometerChanged(AccelDataModel dataModel) {
        if (this.mPrevAccelModel == null) {
            this.mPrevAccelModel = dataModel;
        } else {
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
        } else {
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
        long time = System.currentTimeMillis();
        switch (event.sensor.getType()) {
            case Sensor.TYPE_ACCELEROMETER:
                float x = event.values[0];
                float y = event.values[1];
                float z = event.values[2];
                float xP = (float) (Math.cos(yawOffset) * x - Math.sin(yawOffset) * y);
                float yP = (float) (Math.sin(yawOffset) * x + Math.cos(yawOffset) * y);
                AccelDataModel accelModel = new AccelDataModel(time, xP, yP, event.values[2]);
                accelerometerChanged(accelModel);
                break;
            case Sensor.TYPE_GYROSCOPE:
                GyroDataModel gyroModel = new GyroDataModel(time, event.values[0], event.values[1], event.values[2]);
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
                mCollectionButton.setEnabled(true);
            }
        });
    }
}