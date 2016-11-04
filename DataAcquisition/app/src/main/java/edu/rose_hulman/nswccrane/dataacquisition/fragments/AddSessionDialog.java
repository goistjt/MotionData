package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Activity;
import android.app.Dialog;
import android.app.DialogFragment;
import android.content.DialogInterface;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.view.View;
import android.widget.Button;
import android.widget.ListAdapter;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import datamodels.SessionModel;
import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;
import edu.rose_hulman.nswccrane.dataacquisition.adapters.TimeframeAdapter;
import sqlite.MotionCollectionDBHelper;

/**
 * Created by Jeremiah Goist on 10/4/2016.
 */
public class AddSessionDialog extends DialogFragment implements View.OnClickListener {
    private Activity mRootActivity;
    ListAdapter mListAdapter;
    private SessionModel motionDataPostBody;
    private MotionCollectionDBHelper motionDB;
    public static final String TAG = "ADD_SESSION_DIALOG";

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        View v = getActivity().getLayoutInflater().inflate(R.layout.dialog_add_session, null);
        builder.setView(v);
        initUIElements(v);
        return builder.create();
    }

    private void populateArrayAdapter() {
        motionDB = new MotionCollectionDBHelper(mRootActivity);
        List<TimeframeDataModel> timeData = motionDB.getAllTimeframesBetween(0L,
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
                final Button selector = ((Button) v.findViewById(R.id.collection_time_selector2));
                new AlertDialog.Builder(getActivity())
                        .setTitle("Select a recording period")
                        .setAdapter(mListAdapter, new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                TimeframeDataModel timeframe = (TimeframeDataModel) mListAdapter.getItem(which);
                                motionDataPostBody = motionDB.getAllDataBetween(timeframe.getStartTime(), timeframe.getEndTime());
                                motionDataPostBody.setStartTime(timeframe.getStartTime());
                                StringBuilder sBuilder = new StringBuilder();

                                DateFormat dateFormat = new SimpleDateFormat("yyyy-mm-dd hh:mm:ss", Locale.US);

                                Date date = new Date(timeframe.getStartTime());
                                String time = dateFormat.format(date);
                                sBuilder.append(String.format("Start: %s\n", time));

                                date = new Date(timeframe.getEndTime());
                                time = dateFormat.format(date);
                                sBuilder.append(String.format("End: %s", time));
                                selector.setText(sBuilder.toString());
                            }
                        }).show();
                break;
        }
    }

    public void setActivity(Activity applicationContext) {
        this.mRootActivity = applicationContext;
    }
}
