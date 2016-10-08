package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Dialog;
import android.app.DialogFragment;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.view.View;

import edu.rose_hulman.nswccrane.dataacquisition.R;

/**
 * Created by Jeremiah Goist on 10/4/2016.
 */
public class AddSessionDialog extends DialogFragment implements View.OnClickListener {
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        View v = getActivity().getLayoutInflater().inflate(R.layout.dialog_add_session, null);
        builder.setView(v);
        v.findViewById(R.id.add_sess_submit_button).setOnClickListener(this);
        return builder.create();
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.add_sess_submit_button:
                dismiss();
                break;
        }
    }
}
