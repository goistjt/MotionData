package edu.rose_hulman.nswccrane.dataacquisition;

import android.support.test.runner.AndroidJUnit4;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;

import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.action.ViewActions.click;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.matcher.ViewMatchers.isDisplayed;
import static android.support.test.espresso.matcher.ViewMatchers.withId;
import static android.support.test.espresso.matcher.ViewMatchers.withText;

@RunWith(AndroidJUnit4.class)
public class MainActivityTest extends JUnitTestCase<MainActivity> {

    public MainActivityTest() {
        super(MainActivity.class);
    }

    @Before
    public void testDefaultStrings() {
        onView(withId(R.id.calibration_button)).check(matches(withText(R.string.calibrate)));
        onView(withId(R.id.collection_button)).check(matches(withText(R.string.collect_data)));
        onView(withId(R.id.export_button)).check(matches(withText(R.string.export_data)));
        onView(withId(R.id.x_accel_text_view)).check(matches(withText(R.string.x_accel_default)));
        onView(withId(R.id.y_accel_text_view)).check(matches(withText(R.string.y_accel_default)));
        onView(withId(R.id.z_accel_text_view)).check(matches(withText(R.string.z_accel_default)));
        onView(withId(R.id.pitch_gyro_text_view)).check(matches(withText(R.string.pitch_gyro_default)));
        onView(withId(R.id.roll_gyro_text_view)).check(matches(withText(R.string.roll_gyro_default)));
        onView(withId(R.id.yaw_gyro_text_view)).check(matches(withText(R.string.yaw_gyro_default)));
    }

    @Test
    public void testCalibrationButtonExists() {
        onView(withId(R.id.calibration_button)).check(matches(isDisplayed()));
    }

    @Test
    public void testCollectionButtonExists() {
        onView(withId(R.id.collection_button)).check(matches(isDisplayed()));
    }

    @Test
    public void testExportButtonExists() {
        onView(withId(R.id.export_button)).check(matches(isDisplayed()));
    }

    @Test
    public void testSensorLabelsExist() {
        onView(withId(R.id.x_accel_text_view)).check(matches(isDisplayed()));
        onView(withId(R.id.y_accel_text_view)).check(matches(isDisplayed()));
        onView(withId(R.id.z_accel_text_view)).check(matches(isDisplayed()));
        onView(withId(R.id.pitch_gyro_text_view)).check(matches(isDisplayed()));
        onView(withId(R.id.yaw_gyro_text_view)).check(matches(isDisplayed()));
        onView(withId(R.id.roll_gyro_text_view)).check(matches(isDisplayed()));
    }

    @Test
    public void testCalibrationDialog() {
        onView(withId(R.id.calibration_button)).perform(click());
        onView(withText(R.string.calibration_dialog_title)).check(matches(isDisplayed()));
        onView(withText(R.string.calibrate)).check(matches(isDisplayed()));
        onView(withText(R.string.cancel)).check(matches(isDisplayed()));
    }

}
