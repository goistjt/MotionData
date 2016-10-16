package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Dialog;
import android.app.DialogFragment;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.view.View;
import android.widget.ListAdapter;

import java.util.List;

import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;
import edu.rose_hulman.nswccrane.dataacquisition.adapters.TimeframeAdapter;
import sqlite.MotionCollectionDBHelper;

/**
 * Created by Jeremiah Goist on 10/4/2016.
 */
public class AddSessionDialog extends DialogFragment implements View.OnClickListener {
    private Context applicationContext;
    ListAdapter mListAdapter;

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        View v = getActivity().getLayoutInflater().inflate(R.layout.dialog_add_session, null);
        builder.setView(v);
        initUIElements(v);
        return builder.create();
    }

    private void populateArrayAdapter() {
        MotionCollectionDBHelper motionDB = new MotionCollectionDBHelper(applicationContext);
        List<TimeframeDataModel> timeData = motionDB.getAllTimeframesBetween(System.currentTimeMillis() - (24 * 60 * 60 * 1000),
                System.currentTimeMillis());
        mListAdapter = new TimeframeAdapter(getActivity(), R.layout.list_item_timespan, timeData);
    }

    private void initUIElements(View v) {
        v.findViewById(R.id.add_sess_submit_button).setOnClickListener(this);
        v.findViewById(R.id.collection_time_selector2).setOnClickListener(this);
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.add_sess_submit_button:
                dismiss();
                break;
            case R.id.collection_time_selector2:
                populateArrayAdapter();
                new AlertDialog.Builder(getActivity())
                        .setTitle("Select a recording period")
                        .setAdapter(mListAdapter, new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                dialog.dismiss();
                            }
                        }).show();
                break;
        }
    }

    public void setApplicationContext(Context applicationContext) {
        this.applicationContext = applicationContext;
    }
}
