package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.AlertDialog;
import android.app.Dialog;
import android.app.DialogFragment;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;

import edu.rose_hulman.nswccrane.dataacquisition.R;

/**
 * Created by Jeremiah Goist on 10/3/2016.
 */

public class ExportDialog extends DialogFragment implements View.OnClickListener {

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        LayoutInflater inflater = getActivity().getLayoutInflater();
        View v = inflater.inflate(R.layout.export_redirect, null);
        builder.setView(v);
        v.findViewById(R.id.new_session_button).setOnClickListener(this);
        v.findViewById(R.id.add_to_session_button).setOnClickListener(this);
        return builder.create();
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.new_session_button:
                NewSessionDialog newSessionDialog = new NewSessionDialog();
                newSessionDialog.show(getFragmentManager(), "new_sess_dialog");
                break;
            case R.id.add_to_session_button:
                AddSessionDialog addSessionDialog = new AddSessionDialog();
                addSessionDialog.show(getFragmentManager(), "add_sess_dialog");
                break;
        }
        dismiss();
    }
}
