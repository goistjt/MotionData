package edu.rose_hulman.nswccrane.dataacquisition.adapters;

import android.content.Context;
import android.support.annotation.NonNull;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import java.util.List;

import datamodels.ResponseSessionModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;

/**
 * Created by goistjt on 11/5/2016.
 */

public class SessionAdapter extends ArrayAdapter<ResponseSessionModel> {
    public SessionAdapter(Context context, int resource, List<ResponseSessionModel> objects) {
        super(context, resource, objects);
    }

    @NonNull
    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        View v = convertView;
        if (v == null) {
            v = LayoutInflater.from(getContext()).inflate(R.layout.list_item_session, null);
        }
        ResponseSessionModel session = getItem(position);
        if (session != null) {
            ((TextView) v.findViewById(R.id.session_desc_label)).setText(getContext().getString(R.string.session_desc_format, session.getDesc()));
            ((TextView) v.findViewById(R.id.session_start_label)).setText(getContext().getString(R.string.start_time_label, session.getDate()));
        }
        return v;
    }
}
