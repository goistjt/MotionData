package edu.rose_hulman.nswccrane.dataacquisition;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.widget.EditText;

import butterknife.BindView;
import butterknife.ButterKnife;

/**
 * Created by Jeremiah Goist on 11/25/2016.
 */
public class SettingsActivity extends AppCompatActivity {
    @BindView(R.id.ip_address_edit)
    EditText mIpAddressView;

    @BindView(R.id.sample_rate_edit)
    EditText mSampleRateView;

    public static final String SETTINGS_IP = "IP_ADDRESS";
    public static final String SETTINGS_RATE = "POLL_RATE";

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        ButterKnife.bind(this);
        SharedPreferences settings = getApplicationContext().getSharedPreferences("Settings", 0);
        String ip = settings.getString(SETTINGS_IP, null);
        if (ip != null) {
            mIpAddressView.setText(ip);
        }
        int rate = settings.getInt(SETTINGS_RATE, -1);
        if (rate != -1) {
            mSampleRateView.setText(String.valueOf(rate));
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.settings_menu, menu);
        return super.onCreateOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case R.id.confirm_settings:
                SharedPreferences settings = getApplicationContext().getSharedPreferences("Settings", 0);
                SharedPreferences.Editor editor = settings.edit();
                if (!mIpAddressView.getText().toString().isEmpty()) {
                    editor.putString(SETTINGS_IP, mIpAddressView.getText().toString());
                }
                if (!mSampleRateView.getText().toString().isEmpty()) {
                    editor.putInt(SETTINGS_RATE, Integer.parseInt(mSampleRateView.getText().toString()));
                }
                editor.apply();
                startActivity(new Intent(this, MainActivity.class));
        }
        return super.onOptionsItemSelected(item);
    }
}
