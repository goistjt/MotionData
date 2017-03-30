package edu.rose_hulman.nswccrane.dataacquisition;

import android.content.DialogInterface;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.annotation.VisibleForTesting;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListView;
import android.widget.Toast;

import java.io.File;
import java.io.FilenameFilter;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import butterknife.BindView;
import butterknife.ButterKnife;
import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.adapters.TimeframeAdapter;
import sqlite.MotionCollectionDBHelper;

public class DeletionActivity extends AppCompatActivity {

    @BindView(R.id.delete_list)
    ListView listView;
    private List<TimeframeDataModel> timeData;
    private TimeframeAdapter adapter;
    private MotionCollectionDBHelper motionDB;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_delete);
        ButterKnife.bind(this);
        initializeDependencies();
        initializeListView();
    }

    /**
     * Populates the {@link ListView} with Timeframes from the database, and assigns a listener
     * which is used to delete data corresponding to various Timeframes
     */
    private void initializeListView() {
        listView.setAdapter(adapter);
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int pos, long l) {
                TimeframeDataModel data = adapter.getItem(pos);
                if (data != null) {
                    displayConfirmation(pos, data);
                }
            }
        });
    }

    /**
     * Closes the deletion activity when there is no more data to delete
     */
    private void autoFinish() {
        if (timeData.isEmpty()) {
            this.finish();
        }
    }

    /**
     * Displays a dialog to confirm/cancel the deletion of the selected data
     *
     * @param pos  position of item pressed in the list
     * @param data data selected to delete
     */
    private void displayConfirmation(final int pos, final TimeframeDataModel data) {
        //TODO: Display a dialog asking for confirmation before delete
        DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss", Locale.US);

        Date date = new Date(data.getStartTime());
        String startTime = dateFormat.format(date);
        String endTime = dateFormat.format(new Date(data.getEndTime()));

        new AlertDialog.Builder(this)
                .setTitle("Warning")
                .setMessage(String.format("Are you sure you wish to delete data starting from %s and ending %s?", startTime, endTime))
                .setPositiveButton("Confirm", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialogInterface, int i) {
                        deleteData(data, pos);
                    }
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    /**
     * Deletes the data at the specified location from the SQLite database
     *
     * @param data the {@link TimeframeDataModel} with the timestamps to be deleted
     * @param pos  position in the list that the data came from
     */
    @VisibleForTesting
    private void deleteData(final TimeframeDataModel data, int pos) {
        motionDB.deleteDataBetween(data.getStartTime(), data.getEndTime());
        timeData.remove(pos);
        deleteFiles(data);
        Log.d("DATA LIST", "onItemClick: " + pos);
        adapter.notifyDataSetChanged();
        autoFinish();
    }

    @VisibleForTesting
    private void deleteFiles(final TimeframeDataModel data) {
        File folder = new File(String.valueOf(getExternalFilesDir("records")));
        File[] files = folder.listFiles(new FilenameFilter() {
            @Override
            public boolean accept(File file, String name) {
                return name.matches(".*" + new SimpleDateFormat("yyyy_MM_dd_HH_mm_ss").format(new Date(data.getStartTime())));
            }
        });
        for (File file : files) {
            if (!file.delete()) {
                Toast.makeText(this, "Unable to delete " + file.getAbsolutePath(), Toast.LENGTH_SHORT).show();
            }
        }
    }

    /**
     * Initializes the database and populates the list of Timeframes
     */
    private void initializeDependencies() {
        motionDB = new MotionCollectionDBHelper(this);
        timeData = motionDB.getAllTimeframesBetween(0, System.currentTimeMillis());
        adapter = new TimeframeAdapter(this, R.layout.list_item_timespan, timeData);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.deletion_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.return_home:
                finish();
                break;
            default:
                //No other cases
        }
        return super.onOptionsItemSelected(item);
    }
}
