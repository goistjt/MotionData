package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Activity;
import android.app.Dialog;
import android.app.DialogFragment;
import android.content.DialogInterface;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.view.View;
import android.widget.Button;
import android.widget.ListAdapter;

import com.google.gson.Gson;

import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

import datamodels.ResponseSessionListModel;
import datamodels.ResponseSessionModel;
import datamodels.SessionModel;
import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;
import edu.rose_hulman.nswccrane.dataacquisition.adapters.SessionAdapter;
import edu.rose_hulman.nswccrane.dataacquisition.adapters.TimeframeAdapter;
import edu.rose_hulman.nswccrane.dataacquisition.utils.DeviceUuidFactory;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import sqlite.MotionCollectionDBHelper;

import static edu.rose_hulman.nswccrane.dataacquisition.fragments.ExportDialog.JSON;

/**
 * Created by Jeremiah Goist on 10/4/2016.
 */
public class AddSessionDialog extends DialogFragment implements View.OnClickListener {
    private Activity mRootActivity;
    ListAdapter mListAdapter;
    private SessionModel motionDataPostBody;
    private MotionCollectionDBHelper motionDB;
    public static final String TAG = "ADD_SESSION_DIALOG";
    private ResponseSessionListModel responseSessionListModel;
    private SessionAdapter mSessionAdapter;
    private Button sessionSelector;
    private Button timeSelector;
    private Button submitButton;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        View v = getActivity().getLayoutInflater().inflate(R.layout.dialog_add_session, null);
        builder.setView(v);
        initUIElements(v);
        responseSessionListModel = (new Gson()).fromJson(getArguments().getString("Sessions"), ResponseSessionListModel.class);
        return builder.create();
    }

    private void populateSessionInfoAdapter() {
        List<ResponseSessionModel> sessions = responseSessionListModel.getSessions();
        mSessionAdapter = new SessionAdapter(getActivity(), R.layout.list_item_session, sessions);
    }

    private void populateTimeFrameAdapter() {
        motionDB = new MotionCollectionDBHelper(mRootActivity);
        List<TimeframeDataModel> timeData = motionDB.getAllTimeframesBetween(0L,
                System.currentTimeMillis());
        mListAdapter = new TimeframeAdapter(getActivity(), R.layout.list_item_timespan, timeData);
    }

    private void initUIElements(View v) {
        sessionSelector = ((Button) v.findViewById(R.id.session_selector));
        timeSelector = ((Button) v.findViewById(R.id.collection_time_selector2));
        submitButton = ((Button) v.findViewById(R.id.add_sess_submit_button));
        sessionSelector.setOnClickListener(this);
        timeSelector.setOnClickListener(this);
        submitButton.setOnClickListener(this);
        submitButton.setEnabled(false);
        sessionSelector.setEnabled(false);
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.add_sess_submit_button:
                motionDataPostBody
                        .setDeviceId(new DeviceUuidFactory(mRootActivity).getDeviceUuid().toString());
                String jsonBody = new Gson().toJson(motionDataPostBody);
                new PostAddSession().execute("http://137.112.233.68:80/addToSession", jsonBody); // TODO: Get IP from settings
                dismiss();
                break;
            case R.id.session_selector:
                populateSessionInfoAdapter();
                new AlertDialog.Builder(getActivity())
                        .setTitle("Select a session to add data to")
                        .setAdapter(mSessionAdapter, new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialogInterface, int which) {
                                ResponseSessionModel session = mSessionAdapter.getItem(which);
                                motionDataPostBody.setSessId(session.getId());
                                String sBuilder = String.format("Description: %s\n", session.getDesc()) +
                                        String.format("Start Time: %s", session.getDate());
                                sessionSelector.setText(sBuilder);
                                submitButton.setEnabled(true);
                            }
                        }).show();
                break;
            case R.id.collection_time_selector2:
                populateTimeFrameAdapter();
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
                                timeSelector.setText(sBuilder.toString());
                                sessionSelector.setEnabled(true);
                            }
                        }).show();
                break;
        }
    }

    public void setActivity(Activity applicationContext) {
        this.mRootActivity = applicationContext;
    }

    private class PostAddSession extends AsyncTask<String, Void, Response> {

        @Override
        protected Response doInBackground(String... params) {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(10, TimeUnit.SECONDS)
                    .writeTimeout(params[1].length() * 10, TimeUnit.MILLISECONDS)
                    .readTimeout(params[1].length() * 10, TimeUnit.MILLISECONDS)
                    .build();
            RequestBody body = RequestBody.create(JSON, params[1]);
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
    }
}
