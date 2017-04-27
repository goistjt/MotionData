package edu.rose_hulman.nswccrane.dataacquisition;

import android.content.Context;
import android.content.SharedPreferences;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.support.annotation.VisibleForTesting;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;

import static edu.rose_hulman.nswccrane.dataacquisition.MainActivity.MS_TO_US;
import static edu.rose_hulman.nswccrane.dataacquisition.SettingsActivity.SETTINGS_RATE;

/**
 * Created by Jeremiah Goist on 9/24/2016.
 */
public class CalibrationActivity extends AppCompatActivity implements SensorEventListener {
    private final int CALIBRATION_TIME = 15;
    public SensorManager mSensorManager;
    public List<Float> xVals;
    public List<Float> yVals;
    public List<Float> zVals;
    public List<Float> pitchVals;
    public List<Float> rollVals;
    public List<Float> yawVals;
    @BindView(R.id.time_remaining)
    TextView mTimeRemaining;
    private int pollRate;
    private float yaw_offset;
    private int currentStage;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_calibration);
        ButterKnife.bind(this);
        currentStage = 1;
        pollRate = getSharedPreferences("Settings", 0).getInt(SETTINGS_RATE, 40);
        yaw_offset = getSharedPreferences(getString(R.string.calibration_prefs), 0).getFloat("yaw_offset", 0f);
        mTimeRemaining.setText(getString(R.string.time_remaining, 1, CALIBRATION_TIME));
        mTimeRemaining.setVisibility(View.VISIBLE);
        initDegreeLists();
        initSensorManager();
        initGyroscope(mSensorManager);
        initLinearAccelerometer(mSensorManager);
        initCountdown();
    }

    private void initCountdown() {
        new CountDownTimer(CALIBRATION_TIME * 1000, 1000) {
            @Override
            public void onTick(long millisUntilFinished) {
                mTimeRemaining.setText(getString(R.string.time_remaining, currentStage, millisUntilFinished / 1000));
            }

            @Override
            public void onFinish() {
                float[] avgAccels = new float[]{calculateMedian(xVals), calculateMedian(yVals), calculateMedian(zVals)};
                SharedPreferences settings = getApplicationContext().getSharedPreferences(getString(R.string.calibration_prefs), 0);
                SharedPreferences.Editor editor = settings.edit();
                switch (currentStage) {
                    case 1:
                        CalibrationActivity.this.mSensorManager.unregisterListener(CalibrationActivity.this);
                        float[] avgGyro = new float[]{calculateMedian(rollVals), calculateMedian(pitchVals), calculateMedian(yawVals)};
                        updateAccelNoise(editor, avgAccels[0], avgAccels[1], avgAccels[2]);
                        updateGyroNoise(editor, avgGyro[0], avgGyro[1], avgGyro[2]);
                        editor.apply();
                        currentStage++;
                        initDegreeLists();
                        initGyroscope(mSensorManager);
                        initGravityAccelerometer(mSensorManager);
                        initCountdown();
                        break;
                    case 2:
                        CalibrationActivity.this.mSensorManager.unregisterListener(CalibrationActivity.this);
                        float[] zOffs = calculateZOffsets(avgAccels);
                        updateAngularOffset(zOffs, editor);
                        editor.apply();
                        CalibrationActivity.this.finish();
                        break;
                }
            }
        }.start();
    }

    @VisibleForTesting
    void initDegreeLists() {
        xVals = new ArrayList<>();
        yVals = new ArrayList<>();
        zVals = new ArrayList<>();
        rollVals = new ArrayList<>();
        pitchVals = new ArrayList<>();
        yawVals = new ArrayList<>();
    }

    private void updateAngularOffset(float[] zOffs, SharedPreferences.Editor editor) {
        editor.putFloat("roll_offset", -zOffs[0]);
        editor.putFloat("pitch_offset", -zOffs[1]);
    }

    private void updateAccelNoise(SharedPreferences.Editor editor, float x, float y, float z) {
        editor.putFloat(getString(R.string.x_threshold), x);
        editor.putFloat(getString(R.string.y_threshold), y);
        editor.putFloat(getString(R.string.z_threshold), z);
    }

    private void updateGyroNoise(SharedPreferences.Editor editor, float roll, float pitch, float yaw) {
        editor.putFloat(getString(R.string.roll_threshold), roll);
        editor.putFloat(getString(R.string.pitch_threshold), pitch);
        editor.putFloat(getString(R.string.yaw_threshold), yaw);
    }

    /**
     * Determines the angle the the phone is offset from the z-plane in the x-, and y-axis using the
     * average force of gravity applied to the x-/y-axis during the calibration period
     *
     * @param floats float[]: [0] = xAvg, [1] = yAvg, [2] = zAvg
     * @return float[]: [0] = xzOffset, [1] = yzOffset
     */
    private float[] calculateZOffsets(float[] floats) {
        float gravity = 9.81F;
        float x = floats[0] < 0 ? Math.max(floats[0], gravity) : Math.min(floats[0], gravity);
        float y = floats[1] < 0 ? Math.max(floats[1], gravity) : Math.min(floats[1], gravity);
        float xzOff = (float) (Math.asin(x / gravity));
        float yzOff = (float) (Math.asin(y / gravity));
        return new float[]{xzOff, yzOff};
    }

    /**
     * Calculates the average of a list of floats. Note: This may overflow if the sum of all floats
     * is larger than {@link Float#MAX_VALUE}
     *
     * @param values {@link List<Float>}
     * @return float containing the average
     */
    public float calculateAverage(List<Float> values) {
        float avg = 0;
        for (Float value : values) {
            avg += value;
        }
        avg = avg / values.size();
        return avg;
    }

    /**
     * Calculates the median of a list of floats.
     *
     * @param values {@link List<Float>}
     * @return float containing the average
     */
    public float calculateMedian(List<Float> values) {
        if (values.isEmpty()) {
            return 0;
        }
        Collections.sort(values);
        int size = values.size();
        // Odd num of elements
        if ((size & 1) == 1) {
            return values.get(values.size() / 2);
        }
        // Even num of elements
        return (values.get((size / 2) - 1) + values.get(size / 2)) / 2;
    }

    private void initLinearAccelerometer(SensorManager sensorManager) {
        if (sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION) != null) {
            Sensor mAccelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);
            sensorManager.registerListener(this, mAccelerometer, pollRate * MS_TO_US);
        } else {
            Log.d("Calibration", "Linear Accelerometer does not exist");
        }
    }

    private void initGravityAccelerometer(SensorManager sensorManager) {
        if (sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER) != null) {
            Sensor mAccelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
            sensorManager.registerListener(this, mAccelerometer, pollRate * MS_TO_US);
        } else {
            Log.d("Calibration", "Linear Accelerometer does not exist");
        }
    }

    private void initGyroscope(SensorManager sensorManager) {
        if (sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE) != null) {
            Sensor mGyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
            sensorManager.registerListener(this, mGyroscope, pollRate * MS_TO_US);
        } else {
            Log.d("Calibration", "Gyroscope does not exist");
        }
    }

    private void initSensorManager() {
        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        switch (event.sensor.getType()) {
            case Sensor.TYPE_ACCELEROMETER:
                // Apply yaw offset
                float xP = (float) (Math.cos(yaw_offset) * event.values[0] - Math.sin(yaw_offset) * event.values[1]);
                float yP = (float) (Math.sin(yaw_offset) * event.values[0] + Math.cos(yaw_offset) * event.values[1]);
                accelerometerChanged(new float[]{xP, yP, event.values[2]});
                break;
            case Sensor.TYPE_LINEAR_ACCELERATION:
                accelerometerChanged(event.values);
                break;
            case Sensor.TYPE_GYROSCOPE:
                gyroscopeChanged(event.values);
                break;
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }

    public void accelerometerChanged(float[] floats) {
        xVals.add(floats[0]);
        yVals.add(floats[1]);
        zVals.add(floats[2]);
    }

    public void gyroscopeChanged(float[] floats) {
        rollVals.add(floats[0]);
        pitchVals.add(floats[1]);
        yawVals.add(floats[2]);
    }
}
