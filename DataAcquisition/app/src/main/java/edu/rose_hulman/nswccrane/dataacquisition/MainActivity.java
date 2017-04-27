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
import android.os.Handler;
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

    public static final int MS_TO_US = 1000;
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
    private float x_noise;
    private float y_noise;
    private float z_noise;
    private float roll_noise;
    private float pitch_noise;
    private float yaw_noise;
    private AccelDataModel mPrevAccelModel;
    private GyroDataModel mPrevGyroModel;
    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private Sensor mGyroscope;
    private MotionCollectionDBHelper mCollectionDBHelper;
    private ExecutorService mToggleButtonService;
    private ExecutorService mCollectionService;
    private boolean mStarted;
    private int pollRate, prevSensor = -1;
    private float yawOffset;
    private float pitchOffset;
    private float rollOffset;

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
            case R.id.delete:
                startActivity(new Intent(this, DeletionActivity.class));
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

    /**
     * Begins collecting data and optionally starts a Timer which automatically stops recording after a specified time
     */
    private void handleRecordingTimer() {
        mCollectionButton.setEnabled(false);
        collectionOn();
        initializeAngularOffsets();
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

    /**
     * Pulls the angular offsets in radians from the shared preferences and stores them for the life of this Activity
     */
    private void initializeAngularOffsets() {
        yawOffset = getSharedPreferences(getString(R.string.calibration_prefs), 0).getFloat("yaw_offset", 0f);
        pitchOffset = getSharedPreferences(getString(R.string.calibration_prefs), 0).getFloat("pitch_offset", 0f);
        rollOffset = getSharedPreferences(getString(R.string.calibration_prefs), 0).getFloat("roll_offset", 0f);
    }

    /**
     * Opens a dialog to choose how to export data
     */
    private void openExportDialog() {
        ExportDialog exportDialog = new ExportDialog();
        exportDialog.setActivity(this);
        exportDialog.show(getFragmentManager(), ExportDialog.TAG);
    }

    /**
     * Opens a dialog to set the yaw angular offset and begin calibration
     */
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


    /**
     * Pulls the noise values from Shared Preferences and stores them for the life of this activity
     */
    private void populatePreservedValues() {
        SharedPreferences sharedPref = this.getSharedPreferences(getString(R.string.calibration_prefs), 0);
        x_noise = sharedPref.getFloat(getString(R.string.x_threshold), getResources().getInteger(R.integer.DEFAULT_X_THRESHOLD));
        y_noise = sharedPref.getFloat(getString(R.string.y_threshold), getResources().getInteger(R.integer.DEFAULT_Y_THRESHOLD));
        z_noise = sharedPref.getFloat(getString(R.string.z_threshold), getResources().getInteger(R.integer.DEFAULT_Z_THRESHOLD));
        pitch_noise = sharedPref.getFloat(getString(R.string.pitch_threshold), getResources().getInteger(R.integer.DEFAULT_PITCH_THRESHOLD));
        roll_noise = sharedPref.getFloat(getString(R.string.roll_threshold), getResources().getInteger(R.integer.DEFAULT_ROLL_THRESHOLD));
        yaw_noise = sharedPref.getFloat(getString(R.string.yaw_threshold), getResources().getInteger(R.integer.DEFAULT_YAW_THRESHOLD));
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

    /**
     * Initializes this Activity as a OnClickListener for multiple UI elements
     */
    private void setupUIElements() {
        mCollectionButton.setOnClickListener(this);
        mCalibrationButton.setOnClickListener(this);
        mExportButton.setOnClickListener(this);
    }

    /**
     * Initializes the required sensors and a pair of {@link Executors} for async data caching/storage
     */
    public void initializeCollectionDependencies() {
        mStarted = false;

        mToggleButtonService = Executors.newFixedThreadPool(getResources().getInteger(R.integer.DEFAULT_TOGGLE_THREADS));
        mCollectionService = Executors.newFixedThreadPool(getResources().getInteger(R.integer.DEFAULT_COLLECTION_THREADS));

        mCollectionDBHelper = new MotionCollectionDBHelper(this);

        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        mAccelerometer = mSensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);
        mGyroscope = mSensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
    }

    /**
     * Closes the {@link Executors} and disables listening to the {@link Sensor}
     */
    public void teardownCollectionDependencies() {
        mStarted = false;

        mToggleButtonService.shutdownNow();
        mCollectionService.shutdownNow();

        mSensorManager.unregisterListener(this);
    }

    /**
     * Ends collection of Accel and Gyro data
     */
    public void collectionOff() {
        mStarted = false;
        mCollectionButton.setText(R.string.collect_data);
        mSensorManager.unregisterListener(this);
        mToggleButtonService.execute(new ServiceShutdownRunnable(this, mCollectionService, mCollectionDBHelper));
    }

    /**
     * Begins collection of Accel and Gyro data
     */
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

    /**
     * Pushes a new record to the database through the collection service
     *
     * @param dataModel {@link AccelDataModel} containing the most recent accelerometer readings
     */
    public void accelerometerChanged(AccelDataModel dataModel) {
//        if (this.mPrevAccelModel == null) {
//            this.mPrevAccelModel = dataModel;
//        } else {
//            handleAccelerometerNoise(dataModel);
//        }
//        this.mPrevAccelModel = dataModel;
        mCollectionService.execute(new AccelRunnable(dataModel, mCollectionDBHelper));
        updateAccelerometerUI(dataModel);
    }

    /**
     * Limits the updating of the accelerometer values if the difference between the current readings and the previous is smaller than the noise values.
     *
     * @param dataModel {@link AccelDataModel} containing the most recent accelerometer readings
     */
    private void handleAccelerometerNoise(AccelDataModel dataModel) {
        if (Math.abs(this.mPrevAccelModel.getX() - dataModel.getX()) < this.x_noise) {
            dataModel.setX(this.mPrevAccelModel.getX());
        }
        if (Math.abs(this.mPrevAccelModel.getY() - dataModel.getY()) < this.y_noise) {
            dataModel.setY(this.mPrevAccelModel.getY());
        }
        if (Math.abs(this.mPrevAccelModel.getZ() - dataModel.getZ()) < this.z_noise) {
            dataModel.setZ(this.mPrevAccelModel.getZ());
        }
    }

    /**
     * Updates the UI to show the most recent Accelerometer readings
     *
     * @param dataModel {@link AccelDataModel} containing the most recent accelerometer readings
     */
    private void updateAccelerometerUI(AccelDataModel dataModel) {
        mXTextView.setText(String.format(Locale.US, getString(R.string.x_format), dataModel.getX()));
        mYTextView.setText(String.format(Locale.US, getString(R.string.y_format), dataModel.getY()));
        mZTextView.setText(String.format(Locale.US, getString(R.string.z_format), dataModel.getZ()));
    }

    /**
     * Pushes a new record to the database through the collection service
     *
     * @param dataModel {@link AccelDataModel} containing the most recent gyroscope readings
     */
    public void gyroscopeChanged(GyroDataModel dataModel) {
//        if (this.mPrevGyroModel == null) {
//            this.mPrevGyroModel = dataModel;
//        } else {
//            handleGyroscopeNoise(dataModel);
//        }
//        this.mPrevGyroModel = dataModel;
        mCollectionService.execute(new GyroRunnable(dataModel, mCollectionDBHelper));
        updateGyroscopeUI(dataModel);
    }

    /**
     * Updates the UI to show the most recent Gyroscope readings
     *
     * @param dataModel {@link GyroDataModel} containing the most recent gyroscope readings
     */
    private void updateGyroscopeUI(GyroDataModel dataModel) {
        mPitchTextView.setText(String.format(Locale.US, getString(R.string.pitch_format), dataModel.getPitch()));
        mRollTextView.setText(String.format(Locale.US, getString(R.string.roll_format), dataModel.getRoll()));
        mYawTextView.setText(String.format(Locale.US, getString(R.string.yaw_format), dataModel.getYaw()));
    }

    /**
     * Limits the updating of the gyroscope values if the difference between the current readings and the previous is smaller than the noise values.
     *
     * @param dataModel {@link GyroDataModel} containing the most recent accelerometer readings
     */
    private void handleGyroscopeNoise(GyroDataModel dataModel) {
        if (Math.abs(this.mPrevGyroModel.getPitch() - dataModel.getPitch()) < this.pitch_noise) {
            dataModel.setPitch(this.mPrevGyroModel.getPitch());
        }
        if (Math.abs(this.mPrevGyroModel.getRoll() - dataModel.getRoll()) < this.roll_noise) {
            dataModel.setRoll(this.mPrevGyroModel.getRoll());
        }
        if (Math.abs(this.mPrevGyroModel.getYaw() - dataModel.getYaw()) < this.yaw_noise) {
            dataModel.setYaw(this.mPrevGyroModel.getYaw());
        }
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        long time = System.currentTimeMillis();
        switch (event.sensor.getType()) {
            case Sensor.TYPE_LINEAR_ACCELERATION:
//                if(prevSensor == Sensor.TYPE_LINEAR_ACCELERATION){
//                    break;
//                }
//                prevSensor = Sensor.TYPE_LINEAR_ACCELERATION;
                float[] accelVals = new float[]{event.values[0] - x_noise,
                        event.values[1] - y_noise,
                        event.values[2] - z_noise};
                float[] valsPrime = calculateAccelRotation(accelVals);
                AccelDataModel accelModel = new AccelDataModel(time, valsPrime[0], valsPrime[1], valsPrime[2]);
                accelerometerChanged(accelModel);
                break;
            case Sensor.TYPE_GYROSCOPE:
//                if(prevSensor == Sensor.TYPE_GYROSCOPE){
//                    break;
//                }
//                prevSensor = Sensor.TYPE_GYROSCOPE;
                GyroDataModel gyroModel = new GyroDataModel(time,
                        event.values[0] - pitch_noise,
                        event.values[1] - roll_noise,
                        event.values[2] - yaw_noise);
                gyroscopeChanged(gyroModel);
            default:
                //Empty
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }

    /**
     * Uses the angular offsets from {@link MainActivity#initializeAngularOffsets()} to rotate the
     * acceleration values around the origin such they are aligned at 0 degrees in every axis on
     * the origin
     *
     * @param values The most recent acceleration values
     * @return float[] containing the offset values.
     */
    private float[] calculateAccelRotation(float[] values) {
        float x = values[0];
        float y = values[1];
        float z = values[2];
        float xP = (float) (Math.cos(yawOffset) * x - Math.sin(yawOffset) * y);
        float yP = (float) (Math.sin(yawOffset) * x + Math.cos(yawOffset) * y);
        float xP2 = (float) (Math.cos(rollOffset) * xP - Math.sin(rollOffset) * z);
        float zP = (float) (Math.sin(rollOffset) * xP + Math.cos(rollOffset) * z);
        float yP2 = (float) (Math.cos(pitchOffset) * yP - Math.sin(pitchOffset) * zP);
        float zP2 = (float) (Math.sin(pitchOffset) * -yP + Math.cos(pitchOffset) * -zP);
        return new float[]{xP2, yP2, zP2};
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