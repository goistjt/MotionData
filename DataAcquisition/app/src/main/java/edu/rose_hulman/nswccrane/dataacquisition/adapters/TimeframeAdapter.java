package edu.rose_hulman.nswccrane.dataacquisition.adapters;

import android.content.Context;
import android.support.annotation.NonNull;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ListAdapter;
import android.widget.TextView;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;

/**
 * Created by Jeremiah Goist on 10/13/2016.
 */

public class TimeframeAdapter extends ArrayAdapter<TimeframeDataModel> {
    public TimeframeAdapter(Context context, int resource, List<TimeframeDataModel> objects) {
        super(context, resource, objects);
    }

    @NonNull
    @Override
    public View getView(int position, View convertView, @NonNull ViewGroup parent) {
        View v = convertView;
        if (v == null) {
            v = LayoutInflater.from(getContext()).inflate(R.layout.list_item_timespan, null);
        }
        TimeframeDataModel timeframeDataModel = getItem(position);
        if (timeframeDataModel != null) {
            DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss", Locale.US);

            Date date = new Date(timeframeDataModel.getStartTime());
            String time = dateFormat.format(date);
            ((TextView) v.findViewById(R.id.start_time_label)).setText(getContext().getString(R.string.start_time_label, time));

            date = new Date(timeframeDataModel.getEndTime());
            time = dateFormat.format(date);
            ((TextView) v.findViewById(R.id.end_time_label)).setText(getContext().getString(R.string.end_time_label, time));
        }
        return v;
    }
}
