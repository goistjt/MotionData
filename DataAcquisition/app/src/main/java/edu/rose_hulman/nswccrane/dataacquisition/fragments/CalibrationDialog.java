package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Dialog;
import android.app.DialogFragment;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.view.View;

import edu.rose_hulman.nswccrane.dataacquisition.CalibrationActivity;
import edu.rose_hulman.nswccrane.dataacquisition.R;

/**
 * Created by goistjt on 10/18/2016.
 */

public class CalibrationDialog extends DialogFragment implements View.OnClickListener {
    public static final String TAG = "CALIBRATION_DIALOG";

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        View v = getActivity().getLayoutInflater().inflate(R.layout.dialog_calibrate, null);
        builder.setView(v);
        initUIElements(v);
        return builder.create();
    }

    private void initUIElements(View v) {
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
                Intent startCalibrationIntent = new Intent(getActivity(), CalibrationActivity
                        .class);
                startActivity(startCalibrationIntent);
                this.dismiss();
        }
    }
}
