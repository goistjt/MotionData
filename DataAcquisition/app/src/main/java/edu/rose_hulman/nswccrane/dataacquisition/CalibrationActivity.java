package edu.rose_hulman.nswccrane.dataacquisition;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.TextView;

import butterknife.BindView;
import butterknife.ButterKnife;

/**
 * Created by Jeremiah Goist on 9/24/2016.
 */
public class CalibrationActivity extends AppCompatActivity {
    @BindView(R.id.time_remaining)
    TextView mTimeRemaining;

    private final int CALIBRATION_TIME = 30;
    private SensorManager mSensorManager;
    private Sensor mAccelerometer;
    private Sensor mGyroscope;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_calibration);
        ButterKnife.bind(this);
        mTimeRemaining.setText(getString(R.string.time_remaining, CALIBRATION_TIME));
        mTimeRemaining.setVisibility(View.VISIBLE);
        initSensors();
    }

    public SensorManager getSensorManager() {
        return mSensorManager;
    }

    private void initSensors() {
        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
    }

    public Sensor getAccelerometer() {
        return mAccelerometer;
    }

    public Sensor getGyroscope() {
        return mGyroscope;
    }
}
