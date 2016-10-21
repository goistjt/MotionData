package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Activity;
import android.app.Dialog;
import android.app.DialogFragment;
import android.content.Context;
import android.content.DialogInterface;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import android.view.View;
import android.widget.ListAdapter;
import android.widget.Toast;

import org.androidannotations.annotations.EFragment;

import java.io.IOException;
import java.util.List;

import datamodels.SessionModel;
import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;
import edu.rose_hulman.nswccrane.dataacquisition.adapters.TimeframeAdapter;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import sqlite.MotionCollectionDBHelper;

/**
 * Created by Jeremiah Goist on 10/4/2016.
 */

@EFragment
public class NewSessionDialog extends DialogFragment implements View.OnClickListener {
    ListAdapter mListAdapter;
    private Activity mRootActivity;
    private MotionCollectionDBHelper motionDB;
    public static final String TAG = "NEW_SESSION_DIALOG";

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
        return builder.create();
    }

    private void populateArrayAdapter() {
        motionDB = new MotionCollectionDBHelper(mRootActivity);
        List<TimeframeDataModel> timeData = motionDB.getAllTimeframesBetween(0,
                System.currentTimeMillis());
        mListAdapter = new TimeframeAdapter(getActivity(), R.layout.list_item_timespan, timeData);
    }

    private void initUIElements(View v) {
        v.findViewById(R.id.new_sess_submit_button).setOnClickListener(this);
        v.findViewById(R.id.collection_time_selector).setOnClickListener(this);
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.new_sess_submit_button:
//                new PostNewSession().execute("http://six-dof.csse.rose-hulman.edu/hello-world");
                dismiss();
                break;
            case R.id.collection_time_selector:
                populateArrayAdapter();
                new AlertDialog.Builder(getActivity())
                        .setTitle("Select a recording period")
                        .setAdapter(mListAdapter, new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                TimeframeDataModel timeframe = (TimeframeDataModel) mListAdapter.getItem(which);
                                long start = timeframe.getStartTime();
                                long end = timeframe.getEndTime();
                                Log.v("Time_Selector", String.format("Start: %d\tEnd: %d", start, end));
                                SessionModel sm = motionDB.getAllDataBetween(start, 32165879874632L);
                                dialog.dismiss();
                            }
                        }).show();
                break;
        }
    }

    public void setActivity(Activity applicationContext) {
        this.mRootActivity = applicationContext;
    }

    private class PostNewSession extends AsyncTask<String, Void, Response> {

        @Override
        protected Response doInBackground(String... params) {
            OkHttpClient client = new OkHttpClient();
            Request request = new Request.Builder()
                    .url(params[0])
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
            if (response != null) {
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
}
