package edu.rose_hulman.nswccrane.dataacquisition;

import android.content.SharedPreferences;
import android.support.test.espresso.action.ViewActions;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;

import static android.support.test.InstrumentationRegistry.getInstrumentation;
import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.Espresso.openActionBarOverflowOrOptionsMenu;
import static android.support.test.espresso.action.ViewActions.click;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.matcher.ViewMatchers.withId;
import static android.support.test.espresso.matcher.ViewMatchers.withText;

/**
 * Created by Jeremiah Goist on 11/25/2016.
 */

public class SettingsActvityTest extends JUnitTestCase<SettingsActivity> {
    private SettingsActivity mActivity;

    public SettingsActvityTest() {
        super(SettingsActivity.class);
    }

    @Before
    public void getActivity() {
        mActivity = (SettingsActivity) getCurrentActivity();
    }

    @Before
    public void clearSharedPrefs() {
        SharedPreferences prefs = mActivity.getSharedPreferences("Settings", 0);
        SharedPreferences.Editor editor = prefs.edit();
        editor.putString("IP_ADDRESS", null);
        editor.apply();
    }

    @Test
    public void confirmPrefs() {
        onView(withId(R.id.ip_address_edit)).perform(ViewActions.typeText("192.168.1.1"));
        onView(withId(R.id.ip_address_edit)).check(matches(withText("192.168.1.1")));
        openActionBarOverflowOrOptionsMenu(mActivity);
        onView(withText("Confirm")).perform(click());
        Assert.assertEquals("192.168.1.1", mActivity.getSharedPreferences("Settings", 0).getString("IP_ADDRESS", null));
    }
}
