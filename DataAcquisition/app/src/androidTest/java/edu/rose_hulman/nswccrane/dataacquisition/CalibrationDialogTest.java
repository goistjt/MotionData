package edu.rose_hulman.nswccrane.dataacquisition;

import org.junit.Before;
import org.junit.Test;

import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;

import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.action.ViewActions.click;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.matcher.ViewMatchers.isDisplayed;
import static android.support.test.espresso.matcher.ViewMatchers.withId;
import static android.support.test.espresso.matcher.ViewMatchers.withText;

/**
 * Created by Jeremiah Goist on 9/24/2016.
 */

public class CalibrationDialogTest extends JUnitTestCase<MainActivity> {
    public CalibrationDialogTest() {
        super(MainActivity.class);
    }

    @Before
    public void openCalibrationDialog() {
        onView(withId(R.id.calibration_button)).perform(click());
        onView(withText(R.string.calibration_dialog_title)).check(matches(isDisplayed()));
    }

    @Test
    public void testCalibrationDialog() {
        onView(withText(R.string.calibrate)).check(matches(isDisplayed()));
        onView(withText(R.string.cancel)).check(matches(isDisplayed()));
    }

    @Test
    public void testCancelButton() {
        onView(withId(android.R.id.button2)).perform(click());
        onView(withId(R.id.calibration_button)).check(matches(isDisplayed()));
    }

    @Test
    public void testCalibrateButton() {
        onView(withId(android.R.id.button1)).perform(click());
        onView(withId(R.id.calibration_text)).check(matches(isDisplayed()));
    }
}
