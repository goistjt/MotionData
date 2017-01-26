package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Dialog;
import android.app.DialogFragment;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.annotation.VisibleForTesting;
import android.support.v7.app.AlertDialog;
import android.view.View;

import devadvance.circularseekbar.CircularSeekBar;
import edu.rose_hulman.nswccrane.dataacquisition.CalibrationActivity;
import edu.rose_hulman.nswccrane.dataacquisition.R;

/**
 * Created by goistjt on 10/18/2016.
 */

public class CalibrationDialog extends DialogFragment implements View.OnClickListener {
    public static final String TAG = "CALIBRATION_DIALOG";

    CircularSeekBar mSeekBar;

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        View v = getActivity().getLayoutInflater().inflate(R.layout.dialog_calibrate, null);
        builder.setView(v);
        initUIElements(v);
        return builder.create();
    }

    private void initUIElements(View v) {
        mSeekBar = (CircularSeekBar) v.findViewById(R.id.circularSeekBar1);
        v.findViewById(R.id.calibrate_cancel_dialog_button).setOnClickListener(this);
        v.findViewById(R.id.calibrate_accept_dialog_button).setOnClickListener(this);
    }

    @Override
    public void onClick(View view) {
        switch (view.getId()) {
            case R.id.calibrate_cancel_dialog_button:
                this.dismiss();
                break;
            case R.id.calibrate_accept_dialog_button:
                setYawOffset(calculateYawOffset());
                Intent startCalibrationIntent = new Intent(getActivity(), CalibrationActivity
                        .class);
                startActivity(startCalibrationIntent);
                this.dismiss();
        }
    }

    @VisibleForTesting
    private void setYawOffset(int offset) {
        SharedPreferences prefs = getActivity().getSharedPreferences(getString(R.string.calibration_prefs), 0);
        SharedPreferences.Editor editor = prefs.edit();
        editor.putFloat("yaw_offset", (float) Math.toRadians(offset));
        editor.apply();
    }

    private int calculateYawOffset() {
        return mSeekBar.getProgressAngle();
    }
}
