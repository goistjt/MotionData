package edu.rose_hulman.nswccrane.dataacquisition.fragments;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.app.DialogFragment;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Toast;

import com.google.gson.Gson;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

import edu.rose_hulman.nswccrane.dataacquisition.R;
import edu.rose_hulman.nswccrane.dataacquisition.utils.DeviceUuidFactory;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/**
 * Created by Jeremiah Goist on 10/3/2016.
 */

public class ExportDialog extends DialogFragment implements View.OnClickListener {

    private Activity mRootActivity;
    public static final String TAG = "EXPORT_DIALOG";
    public static final MediaType JSON
            = MediaType.parse("application/json; charset=utf-8");

    public void setActivity(Activity mApplicationContext) {
        this.mRootActivity = mApplicationContext;
    }

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
                newSessionDialog.setActivity(mRootActivity);
                newSessionDialog.show(mRootActivity.getFragmentManager(), NewSessionDialog.TAG);
                break;
            case R.id.add_to_session_button:
                Toast.makeText(mRootActivity, "Retrieving existing Sessions from the server", Toast.LENGTH_SHORT).show();
                (new AddSessionTask()).execute("http://137.112.233.68:80/getSessions/" + (new DeviceUuidFactory(mRootActivity)).getDeviceUuid().toString());
                break;
        }
        dismiss();
    }

    private class AddSessionTask extends AsyncTask<String, Void, Response> {

        @Override
        protected Response doInBackground(String... params) {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(5, TimeUnit.SECONDS)
                    .readTimeout(5, TimeUnit.SECONDS)
                    .build();
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
            Bundle args = new Bundle();
            try {
                if (response != null) {
                    args.putString("Sessions", response.body().string());
                    AddSessionDialog dialog = new AddSessionDialog();
                    dialog.setActivity(mRootActivity);
                    // Supply index input as an argument.
                    dialog.setArguments(args);
                    dialog.show(mRootActivity.getFragmentManager(), AddSessionDialog.TAG);
                } else {
                    Toast.makeText(mRootActivity, "Unable to retrieve existing Sessions from the server", Toast.LENGTH_SHORT).show();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}