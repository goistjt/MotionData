package edu.rose_hulman.nswccrane.dataacquisition;

import android.support.test.runner.AndroidJUnit4;

import org.junit.Test;
import org.junit.runner.RunWith;

import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;

import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.matcher.ViewMatchers.isDisplayed;
import static android.support.test.espresso.matcher.ViewMatchers.withId;

/**
 * Created by goistjt on 9/17/2016.
 */
@RunWith(AndroidJUnit4.class)
public class MainActivityTest extends JUnitTestCase<MainActivity> {

    public MainActivityTest() {
        super(MainActivity.class);
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

}
