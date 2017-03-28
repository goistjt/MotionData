package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Activity;
import android.app.Dialog;
import android.app.DialogFragment;
import android.content.Context;
import android.content.DialogInterface;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListAdapter;
import android.widget.Toast;

import com.google.gson.Gson;

import org.androidannotations.annotations.EFragment;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import datamodels.SessionModel;
import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;
import edu.rose_hulman.nswccrane.dataacquisition.adapters.TimeframeAdapter;
import edu.rose_hulman.nswccrane.dataacquisition.utils.DeviceUuidFactory;
import edu.rose_hulman.nswccrane.dataacquisition.utils.StringComressor;
import sqlite.MotionCollectionDBHelper;

import static edu.rose_hulman.nswccrane.dataacquisition.SettingsActivity.SETTINGS_NAME;

/**
 * Created by Steve Trotta on 3/11/2017.
 */

@EFragment
public class SaveRecordLocallyDialog extends DialogFragment implements View.OnClickListener {

    public static final String TAG = "SAVE_RECORD_LOCALLY_DIALOG";
    private static final String SEPARATOR = "_";
    private ListAdapter mListAdapter;
    private Activity mRootActivity;
    private MotionCollectionDBHelper motionDB;
    private SessionModel motionDataPostBody;
    private EditText mRecordNameText;
    private boolean selected_time;

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
    }

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        View v = getActivity().getLayoutInflater().inflate(R.layout.dialog_save_record_locally, null);
        builder.setView(v);
        initUIElements(v);
        selected_time = false;
        return builder.create();
    }

    private void populateArrayAdapter() {
        motionDB = new MotionCollectionDBHelper(mRootActivity);
        List<TimeframeDataModel> timeData = motionDB.getAllTimeframesBetween((long) 0, System.currentTimeMillis());
        mListAdapter = new TimeframeAdapter(getActivity(), R.layout.list_item_timespan, timeData);
    }

    private void initUIElements(View v) {
        v.findViewById(R.id.save_record_locally_submit_button).setOnClickListener(this);
        v.findViewById(R.id.collection_time_selector).setOnClickListener(this);
        mRecordNameText = (EditText) v.findViewById(R.id.name_edit_text);
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.save_record_locally_submit_button:
                if(!selected_time) {
                    Toast.makeText(mRootActivity, "Record NOT Saved. " +
                            "Must pick a time-frame for the record.",
                            Toast.LENGTH_SHORT).show();
                    break;
                }
                String deviceUuid = new DeviceUuidFactory(mRootActivity).getDeviceUuid().toString();
                String recordName = mRecordNameText.getText().toString();
                motionDataPostBody
                        .setDeviceId(deviceUuid)
                        .setDeviceName(mRootActivity.getSharedPreferences("Settings", 0)
                        .getString(SETTINGS_NAME,""))
                        .setSessDesc(recordName);
                try{
                    String jsonBody = new Gson().toJson(motionDataPostBody);
                    new PostSaveRecordLocally().execute(recordName, jsonBody);
                }
                catch(Exception e) {
                    Toast.makeText(mRootActivity, "Record NOT Saved. Error in serialization.",
                            Toast.LENGTH_SHORT).show();
                    break;
                }
                dismiss();
                break;
            case R.id.collection_time_selector:
                final Button selector = (Button) v.findViewById(R.id.collection_time_selector);
                populateArrayAdapter();
                new AlertDialog.Builder(getActivity())
                        .setTitle("Select a recording period")
                        .setAdapter(mListAdapter, new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                TimeframeDataModel timeframe = (TimeframeDataModel)
                                        mListAdapter.getItem(which);
                                motionDataPostBody = motionDB.getAllDataBetween(
                                        timeframe.getStartTime(), timeframe.getEndTime());
                                motionDataPostBody.setStartTime(timeframe.getStartTime());
                                StringBuilder sBuilder = new StringBuilder();

                                DateFormat dateFormat = new SimpleDateFormat("yyyy-mm-dd hh:mm:ss",
                                        Locale.US);

                                Date date = new Date(timeframe.getStartTime());
                                String time = dateFormat.format(date);
                                sBuilder.append(String.format("Start: %s\n", time));

                                date = new Date(timeframe.getEndTime());
                                time = dateFormat.format(date);
                                sBuilder.append(String.format("End: %s", time));
                                selector.setText(sBuilder.toString());
                                selected_time = true;
                            }
                        }).show();
                break;
        }
    }

    public void setActivity(Activity applicationContext) {
        this.mRootActivity = applicationContext;
    }

    private class PostSaveRecordLocally extends AsyncTask<String, Void, Boolean> {
        @Override
        protected Boolean doInBackground(String... params) {
            try {
                String timeStamp = new SimpleDateFormat("yyyy_MM_dd_HH_mm_ss").format(new Date());
                // This is replacing all non-alphanumeric characters with the empty string for names
                File myExternalFile = new File(mRootActivity.getExternalFilesDir("records"),
                        String.valueOf(params[0]).replaceAll("[^a-zA-Z0-9]", "").concat(SEPARATOR)
                                .concat(timeStamp)
                );
                FileOutputStream fos = new FileOutputStream(myExternalFile);
                fos.write(StringComressor.compressString(params[1]).getBytes());
                fos.close();
                return true;
            } catch (IOException e) {
                e.printStackTrace();
                Toast.makeText(mRootActivity, "Record NOT Saved. Error while saving.",
                        Toast.LENGTH_SHORT).show();
                return false;
            }
        }

        @Override
        protected void onPostExecute(Boolean response) {
            if (response != null && response) {
                Toast.makeText(mRootActivity, "Record Saved Successfully.", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(mRootActivity, "Record NOT Saved.", Toast.LENGTH_SHORT).show();
            }
        }
    }
}