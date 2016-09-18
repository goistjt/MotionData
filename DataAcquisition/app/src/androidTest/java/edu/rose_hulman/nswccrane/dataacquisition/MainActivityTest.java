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

}
