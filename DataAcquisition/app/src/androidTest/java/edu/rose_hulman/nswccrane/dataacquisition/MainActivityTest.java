package edu.rose_hulman.nswccrane.dataacquisition;

import org.junit.Test;

import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.matcher.ViewMatchers.isDisplayed;

/**
 * Created by goistjt on 9/17/2016.
 */
public class MainActivityTest {

    @Test
    public void testCalibrationButtonExists() {
        onView(withId(R.id.calibration_button)).check(matches(isDisplayed()));
    }

}
