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
    public static final String SETTINGS_IP = "IP_ADDRESS";
    public static final String SETTINGS_RATE = "POLL_RATE";
    public static final String SETTINGS_NAME = "DEVICE_NAME";
    @BindView(R.id.ip_address_edit)
    EditText mIpAddressView;
    @BindView(R.id.sample_rate_edit)
    EditText mSampleRateView;
    @BindView(R.id.device_name_edit)
    EditText mDeviceName;
    private SharedPreferences preferences;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        ButterKnife.bind(this);
        preferences = getApplicationContext().getSharedPreferences("Settings", 0);
        populateSettings();
    }

    /**
     * Updates the UI with existing values from the Shared Preferences
     */
    private void populateSettings() {
        String ip = preferences.getString(SETTINGS_IP, null);
        if (ip != null) {
            mIpAddressView.setText(ip);
        }
        int rate = preferences.getInt(SETTINGS_RATE, -1);
        if (rate != -1) {
            mSampleRateView.setText(String.valueOf(rate));
        }
        String name = preferences.getString(SETTINGS_NAME, null);
        if (name != null) {
            mDeviceName.setText(name);
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
                preferences = getApplicationContext().getSharedPreferences("Settings", 0);
                SharedPreferences.Editor editor = preferences.edit();
                updateIpAddress(editor);
                updateCollectionRate(editor);
                updateDeviceName(editor);
                editor.apply();
                startActivity(new Intent(this, MainActivity.class));
        }
        return super.onOptionsItemSelected(item);
    }

    /**
     * Updates the user defined device name in Shared Preferences
     *
     * @param editor {@link android.content.SharedPreferences.Editor}
     */
    private void updateDeviceName(SharedPreferences.Editor editor) {
        if (!mDeviceName.getText().toString().isEmpty()) {
            editor.putString(SETTINGS_NAME, mDeviceName.getText().toString());
        }
    }

    /**
     * Updates the user defined collection rate in Shared Preferences
     *
     * @param editor {@link android.content.SharedPreferences.Editor}
     */
    private void updateCollectionRate(SharedPreferences.Editor editor) {
        if (!mSampleRateView.getText().toString().isEmpty()) {
            int rate = Integer.parseInt(mSampleRateView.getText().toString());
            if (rate > 0) {
                editor.putInt(SETTINGS_RATE, Integer.parseInt(mSampleRateView.getText().toString()));
            }
        }
    }

    /**
     * Updates the server's Ip Address in Shared Preferences
     *
     * @param editor {@link android.content.SharedPreferences.Editor}
     */
    private void updateIpAddress(SharedPreferences.Editor editor) {
        if (!mIpAddressView.getText().toString().isEmpty()) {
            editor.putString(SETTINGS_IP, mIpAddressView.getText().toString());
        }
    }
}
