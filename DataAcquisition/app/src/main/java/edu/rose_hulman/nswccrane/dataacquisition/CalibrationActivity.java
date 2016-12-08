package edu.rose_hulman.nswccrane.dataacquisition;

import android.content.Context;
import android.content.SharedPreferences;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import butterknife.BindView;
import butterknife.ButterKnife;

import static edu.rose_hulman.nswccrane.dataacquisition.MainActivity.MS_TO_US;
import static edu.rose_hulman.nswccrane.dataacquisition.SettingsActivity.SETTINGS_RATE;

/**
 * Created by Jeremiah Goist on 9/24/2016.
 */
public class CalibrationActivity extends AppCompatActivity implements SensorEventListener {
    @BindView(R.id.time_remaining)
    TextView mTimeRemaining;

    public SensorManager mSensorManager;
    public float max_x_noise = 0;
    public float max_y_noise = 0;
    public float max_z_noise = 0;
    public float max_roll_noise = 0;
    public float max_pitch_noise = 0;
    public float max_yaw_noise = 0;

    private float[] prev_accel = new float[]{0, 0, 0};
    private float[] prev_gyro = new float[]{0, 0, 0};

    private int pollRate;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_calibration);
        ButterKnife.bind(this);
        pollRate = getSharedPreferences("Settings", 0).getInt(SETTINGS_RATE, 40);
        int CALIBRATION_TIME = 30;
        mTimeRemaining.setText(getString(R.string.time_remaining, CALIBRATION_TIME));
        mTimeRemaining.setVisibility(View.VISIBLE);
        initSensorManager();
        initAccelerometer(mSensorManager);
        initGyroscope(mSensorManager);
        new CountDownTimer(CALIBRATION_TIME * 1000, 1000) {
            @Override
            public void onTick(long millisUntilFinished) {
                mTimeRemaining.setText(getString(R.string.time_remaining, millisUntilFinished / 1000));
            }

            @Override
            public void onFinish() {
                CalibrationActivity.this.mSensorManager.unregisterListener(CalibrationActivity.this);
                SharedPreferences settings = getApplicationContext().getSharedPreferences(getString(R.string.calibration_prefs), 0);
                SharedPreferences.Editor editor = settings.edit();
                editor.putFloat(getString(R.string.x_threshold), max_x_noise);
                editor.putFloat(getString(R.string.y_threshold), max_y_noise);
                editor.putFloat(getString(R.string.z_threshold), max_z_noise);
                editor.putFloat(getString(R.string.roll_threshold), max_roll_noise);
                editor.putFloat(getString(R.string.pitch_threshold), max_pitch_noise);
                editor.putFloat(getString(R.string.yaw_threshold), max_yaw_noise);
                editor.apply();
                CalibrationActivity.this.finish();
            }
        }.start();
    }

    private void initAccelerometer(SensorManager sensorManager) {
        if (sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION) != null) {
            Sensor mAccelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);
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
        max_x_noise = Math.abs(Math.max(max_x_noise, floats[0] - prev_accel[0]));
        max_y_noise = Math.abs(Math.max(max_y_noise, floats[1] - prev_accel[1]));
        max_z_noise = Math.abs(Math.max(max_z_noise, floats[2] - prev_accel[2]));
        prev_accel = floats;
    }

    public void gyroscopeChanged(float[] floats) {
        max_roll_noise = Math.abs(Math.max(max_roll_noise, floats[0] - prev_gyro[0]));
        max_pitch_noise = Math.abs(Math.max(max_pitch_noise, floats[1] - prev_gyro[1]));
        max_yaw_noise = Math.abs(Math.max(max_yaw_noise, floats[2] - prev_gyro[2]));
        prev_gyro = floats;
    }
}
