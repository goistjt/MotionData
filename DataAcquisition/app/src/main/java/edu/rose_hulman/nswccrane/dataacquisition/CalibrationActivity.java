package edu.rose_hulman.nswccrane.dataacquisition;

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

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_calibration);
        ButterKnife.bind(this);
        mTimeRemaining.setText(getString(R.string.time_remaining, CALIBRATION_TIME));
        mTimeRemaining.setVisibility(View.VISIBLE);
    }
}
