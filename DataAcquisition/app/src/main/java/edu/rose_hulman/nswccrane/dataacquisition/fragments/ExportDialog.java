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
        builder.setView(inflater.inflate(R.layout.export_redirect, null));
        return builder.create();
    }
    @Override
    public void onClick(View v) {
        // TODO: Implement this for the buttons
    }
}
