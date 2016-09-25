package edu.rose_hulman.nswccrane.dataacquisition;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import butterknife.BindView;
import butterknife.ButterKnife;

/**
 * Created by Jeremiah Goist on 9/24/2016.
 */
public class CalibrationActivity extends AppCompatActivity implements SensorEventListener {
    @BindView(R.id.time_remaining)
    TextView mTimeRemaining;

    private final int CALIBRATION_TIME = 30;
    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private Sensor mGyroscope;
    public float max_x_noise = 0;
    public float max_y_noise = 0;
    public float max_z_noise = 0;
    public float max_roll_noise = 0;
    public float max_pitch_noise = 0;
    public float max_yaw_noise = 0;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_calibration);
        ButterKnife.bind(this);
        mTimeRemaining.setText(getString(R.string.time_remaining, CALIBRATION_TIME));
        mTimeRemaining.setVisibility(View.VISIBLE);
        initSensorManager();
        initAccelerometer(mSensorManager);
        initGyroscope(mSensorManager);
    }

    private void initAccelerometer(SensorManager sensorManager) {
        if (sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION) != null) {
            mAccelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);
        } else {
            Log.d("Calibration", "Linear Accelerometer does not exist");
        }
    }

    private void initGyroscope(SensorManager sensorManager) {
        if (sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE) != null) {
            mGyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
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
                break;
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {

    }

    public void accelerometerChanged(float[] floats) {
        max_x_noise = Math.abs(Math.max(max_x_noise, floats[0]));
        max_y_noise = Math.abs(Math.max(max_y_noise, floats[1]));
        max_z_noise = Math.abs(Math.max(max_z_noise, floats[2]));
    }

    public void gyroscopeChanged(float[] floats) {

    }
}
