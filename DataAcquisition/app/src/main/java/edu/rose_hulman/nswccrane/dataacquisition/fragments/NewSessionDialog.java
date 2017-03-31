package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Activity;
import android.app.Dialog;
import android.app.DialogFragment;
import android.content.Context;
import android.content.DialogInterface;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.support.annotation.VisibleForTesting;
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
import java.util.concurrent.TimeUnit;

import datamodels.SessionModel;
import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;
import edu.rose_hulman.nswccrane.dataacquisition.adapters.TimeframeAdapter;
import edu.rose_hulman.nswccrane.dataacquisition.utils.DeviceUuidFactory;
import edu.rose_hulman.nswccrane.dataacquisition.utils.StringComressor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import sqlite.MotionCollectionDBHelper;

import static edu.rose_hulman.nswccrane.dataacquisition.SettingsActivity.SETTINGS_IP;
import static edu.rose_hulman.nswccrane.dataacquisition.SettingsActivity.SETTINGS_NAME;
import static edu.rose_hulman.nswccrane.dataacquisition.fragments.ExportDialog.JSON;

/**
 * Created by Jeremiah Goist on 10/4/2016.
 */

@EFragment
public class NewSessionDialog extends DialogFragment implements View.OnClickListener {
    public static final String TAG = "NEW_SESSION_DIALOG";
    private static final String SEPARATOR = "_";

    private ListAdapter mListAdapter;
    private Activity mRootActivity;
    private MotionCollectionDBHelper motionDB;
    private SessionModel motionDataPostBody;
    private EditText mSessionDescriptionText;
    private boolean selectedTime;
    private long recordingTime;

    private static boolean isExternalStorageReadOnly() {
        String extStorageState = Environment.getExternalStorageState();
        return Environment.MEDIA_MOUNTED_READ_ONLY.equals(extStorageState);
    }

    private static boolean isExternalStorageAvailable() {
        String extStorageState = Environment.getExternalStorageState();
        return Environment.MEDIA_MOUNTED.equals(extStorageState);
    }

    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
    }

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        View v = getActivity().getLayoutInflater().inflate(R.layout.dialog_new_session, null);
        builder.setView(v);
        initUIElements(v);
        selectedTime = false;
        return builder.create();
    }

    private void populateArrayAdapter() {
        motionDB = new MotionCollectionDBHelper(mRootActivity);
        List<TimeframeDataModel> timeData = motionDB.getAllTimeframesBetween((long) 0, System.currentTimeMillis());
        mListAdapter = new TimeframeAdapter(getActivity(), R.layout.list_item_timespan, timeData);
    }

    private void initUIElements(View v) {
        v.findViewById(R.id.new_sess_submit_button).setOnClickListener(this);
        v.findViewById(R.id.collection_time_selector).setOnClickListener(this);
        if (isExternalStorageAvailable() && !isExternalStorageReadOnly()) {
            v.findViewById(R.id.save_record_locally_button).setOnClickListener(this);
        }
        mSessionDescriptionText = (EditText) v.findViewById(R.id.description_edit_text);
    }

    @Override
    public void onClick(View v) {
        if (!selectedTime && v.getId() != R.id.collection_time_selector) {
            Toast.makeText(mRootActivity, "Record NOT Saved. " +
                            "Must pick a time-frame for the record.",
                    Toast.LENGTH_SHORT).show();
            return;
        }
        switch (v.getId()) {
            case R.id.save_record_locally_button:
                String deviceUuid = new DeviceUuidFactory(mRootActivity).getDeviceUuid().toString();
                String recordName = mSessionDescriptionText.getText().toString();
                motionDataPostBody
                        .setDeviceId(deviceUuid)
                        .setDeviceName(mRootActivity.getSharedPreferences("Settings", 0)
                                .getString(SETTINGS_NAME, ""))
                        .setSessDesc(recordName);
                try {
                    String jsonBody = new Gson().toJson(motionDataPostBody);
                    new PostSaveRecordLocally().execute(recordName, jsonBody);
                } catch (Exception e) {
                    Toast.makeText(mRootActivity, "Record NOT Saved. Error in serialization.",
                            Toast.LENGTH_SHORT).show();
                    break;
                }
                dismiss();
                break;
            case R.id.new_sess_submit_button:
                motionDataPostBody
                        .setDeviceId(new DeviceUuidFactory(mRootActivity).getDeviceUuid().toString())
                        .setDeviceName(mRootActivity.getSharedPreferences("Settings", 0).getString(SETTINGS_NAME, ""))
                        .setSessDesc(mSessionDescriptionText.getText().toString());
                String jsonBody = new Gson().toJson(motionDataPostBody);
                String ip = mRootActivity.getSharedPreferences("Settings", 0).getString(SETTINGS_IP, null);
                if (ip == null || ip.isEmpty()) { // Don't change this. For some reason it converts null to the empty string
                    Toast.makeText(mRootActivity, "Please enter the Ip Address of the server in the Settings page", Toast.LENGTH_SHORT).show();
                } else {
                    new PostNewSession().execute(String.format("http://%s:80/createSession", ip), jsonBody);
                    dismiss();
                }
                break;
            case R.id.collection_time_selector:
                final Button selector = (Button) v.findViewById(R.id.collection_time_selector);
                populateArrayAdapter();
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
                                recordingTime = timeframe.getStartTime();
                                selectedTime = true;
                            }
                        }).show();
                break;
        }
    }

    public void setActivity(Activity applicationContext) {
        this.mRootActivity = applicationContext;
    }

    /**
     * Writes a file containing the compressed accel and gyro data for a recording to the local storage
     *
     * @param params        0 - Session description, 1 - JSON formatted {@link SessionModel}
     * @param recordingTime Start time of recording
     * @throws IOException if the file is unable to be opened.
     */
    @VisibleForTesting
    private void writeFile(String[] params, long recordingTime) throws IOException {
        String timeStamp = new SimpleDateFormat("yyyy_MM_dd_HH_mm_ss").format(new Date(recordingTime));
        // This is replacing all non-alphanumeric characters with the empty string for names
        File myExternalFile = new File(mRootActivity.getExternalFilesDir("records"),
                String.valueOf(params[0]).replaceAll("[^a-zA-Z0-9]", "").concat(SEPARATOR)
                        .concat(timeStamp)
        );
        FileOutputStream fos = new FileOutputStream(myExternalFile);
        fos.write(StringComressor.compressString(params[1]).getBytes());
        fos.close();
    }

    private class PostNewSession extends AsyncTask<String, Void, Response> {
        @Override
        protected Response doInBackground(String... params) {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(10, TimeUnit.SECONDS)
                    .writeTimeout(params[1].length() * 10, TimeUnit.MILLISECONDS)
                    .readTimeout(params[1].length() * 10, TimeUnit.MILLISECONDS)
                    .build();
            RequestBody body = RequestBody.create(JSON, StringComressor.compressString(params[1]));
            Request request = new Request.Builder()
                    .url(params[0])
                    .post(body)
                    .build();
            try {
                return client.newCall(request).execute();
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }

        @Override
        protected void onPostExecute(Response response) {
            if (response != null && response.isSuccessful()) {
                try {
                    Toast.makeText(mRootActivity, response.body().string(), Toast.LENGTH_SHORT).show();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            } else {
                Toast.makeText(mRootActivity, "No response provided", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private class PostSaveRecordLocally extends AsyncTask<String, Void, Boolean> {
        @Override
        protected Boolean doInBackground(String... params) {
            try {
                writeFile(params, recordingTime);
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
