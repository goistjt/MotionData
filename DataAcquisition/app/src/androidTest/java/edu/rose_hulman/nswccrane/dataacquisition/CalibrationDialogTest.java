package edu.rose_hulman.nswccrane.dataacquisition;

import android.support.test.espresso.action.GeneralLocation;
import android.support.test.espresso.action.Press;
import android.support.test.espresso.action.Tap;
import android.support.test.runner.AndroidJUnit4;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import edu.rose_hulman.nswccrane.dataacquisition.fragments.CalibrationDialog;
import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;
import edu.rose_hulman.nswccrane.dataacquisition.testing_utils.ClickAction;

import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.action.ViewActions.click;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.matcher.ViewMatchers.isDisplayed;
import static android.support.test.espresso.matcher.ViewMatchers.withId;
import static android.support.test.espresso.matcher.ViewMatchers.withText;

/**
 * Created by Jeremiah Goist on 9/24/2016.
 */
@RunWith(AndroidJUnit4.class)
public class CalibrationDialogTest extends JUnitTestCase<MainActivity> {
    public CalibrationDialogTest() {
        super(MainActivity.class);
    }

    @Before
    public void openCalibrationDialog() {
        onView(withId(R.id.calibration_button)).perform(click());
        ExportDialogTest.waitForFragment(CalibrationDialog.TAG, 5000, getCurrentActivity());
        onView(withText(R.string.please_secure_device)).check(matches(isDisplayed()));
    }

    @Test
    public void testCalibrationDialog() {
        onView(withId(R.id.calibrate_accept_dialog_button)).check(matches(isDisplayed()));
        onView(withId(R.id.calibrate_cancel_dialog_button)).check(matches(isDisplayed()));
    }

    @Test
    public void testCancelButton() throws InterruptedException {
        onView(withId(R.id.calibrate_cancel_dialog_button)).perform(new ClickAction(Tap.SINGLE, GeneralLocation.CENTER, Press
                .FINGER, null));
        Thread.sleep(1000);
        onView(withId(R.id.calibration_button)).check(matches(isDisplayed()));
    }

    @Test
    public void testCalibrateButton() throws InterruptedException {
        onView(withId(R.id.calibrate_accept_dialog_button)).perform(new ClickAction(Tap.SINGLE, GeneralLocation.CENTER, Press
                .FINGER, null));
        Thread.sleep(1000);
        onView(withId(R.id.calibration_text)).check(matches(isDisplayed()));
    }
}
