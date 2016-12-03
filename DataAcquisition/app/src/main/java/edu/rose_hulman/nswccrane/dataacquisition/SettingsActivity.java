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

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        ButterKnife.bind(this);
        SharedPreferences settings = getApplicationContext().getSharedPreferences("Settings", 0);
        String ip = settings.getString("IP_ADDRESS", null);
        if (ip != null) {
            mIpAddressView.setText(ip);
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
                editor.putString("IP_ADDRESS", mIpAddressView.getText().toString());
                editor.putInt("POLL_RATE", Integer.parseInt(mSampleRateView.getText().toString()));
                editor.apply();
                startActivity(new Intent(this, MainActivity.class));
        }
        return super.onOptionsItemSelected(item);
    }
}
