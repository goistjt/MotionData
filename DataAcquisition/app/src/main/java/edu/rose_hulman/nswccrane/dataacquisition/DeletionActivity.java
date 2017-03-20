package edu.rose_hulman.nswccrane.dataacquisition;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListView;

import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;
import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.adapters.TimeframeAdapter;
import sqlite.MotionCollectionDBHelper;

public class DeletionActivity extends AppCompatActivity {

    private List<TimeframeDataModel> timeData;
    private TimeframeAdapter adapter;
    private MotionCollectionDBHelper motionDB;
    @BindView(R.id.delete_list)
    ListView listView;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_delete);

        motionDB = new MotionCollectionDBHelper(this);
        timeData = motionDB.getAllTimeframesBetween(0, System.currentTimeMillis());
        adapter = new TimeframeAdapter(this, R.layout.list_item_timespan, timeData);
        ButterKnife.bind(this);
        listView.setAdapter(adapter);

        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int pos, long l) {
                TimeframeDataModel data = adapter.getItem(pos);
                if (data != null) {
                    motionDB.deleteDataBetween(data.getStartTime(), data.getEndTime());
                    timeData.remove(pos);
                    Log.d("DATA LIST", "onItemClick: " + pos);
                    adapter.notifyDataSetChanged();
                }
                if (timeData.isEmpty()) {
                    DeletionActivity.this.finish();
                }
            }
        });
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
