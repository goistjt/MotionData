package edu.rose_hulman.nswccrane.dataacquisition;

import android.app.Activity;
import android.app.Fragment;
import android.os.SystemClock;
import android.support.test.espresso.action.GeneralLocation;
import android.support.test.espresso.action.Press;
import android.support.test.espresso.action.Tap;
import android.support.test.runner.AndroidJUnit4;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import edu.rose_hulman.nswccrane.dataacquisition.fragments.AddSessionDialog;
import edu.rose_hulman.nswccrane.dataacquisition.fragments.ExportDialog;
import edu.rose_hulman.nswccrane.dataacquisition.fragments.NewSessionDialog;
import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;
import edu.rose_hulman.nswccrane.dataacquisition.testing_utils.ClickAction;

import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.matcher.ViewMatchers.isDisplayed;
import static android.support.test.espresso.matcher.ViewMatchers.withId;
import static android.support.test.espresso.matcher.ViewMatchers.withText;

/**
 * Created by Jeremiah Goist on 10/1/2016.
 */

@RunWith(AndroidJUnit4.class)
public class ExportDialogTest extends JUnitTestCase<MainActivity> {
    public ExportDialogTest() {
        super(MainActivity.class);
    }


    public static Fragment waitForFragment(String tag, int timeout, Activity activity) {
        long endTime = SystemClock.uptimeMillis() + timeout;
        while (SystemClock.uptimeMillis() <= endTime) {
            android.app.Fragment fragment = activity.getFragmentManager().findFragmentByTag(tag);
            if (fragment != null) {
                return fragment;
            }
        }
        return null;
    }


    @Before
    public void openDialog() {
        onView(withId(R.id.export_button)).perform(new ClickAction(Tap.SINGLE, GeneralLocation.CENTER, Press.FINGER, null));
        waitForFragment(ExportDialog.TAG, 5000, getCurrentActivity());
        onView(withId(R.id.new_session_button)).check(matches(withText(R.string.new_session)));
        onView(withId(R.id.add_to_session_button)).check(matches(withText(R.string.add_to_session)));
    }

    @Test
    public void openCloseNewSessionDialog() throws InterruptedException {
//        closeSoftKeyboard();
//        Thread.sleep(1000);
        onView(withId(R.id.new_session_button)).perform(new ClickAction(Tap.SINGLE, GeneralLocation.CENTER, Press.FINGER, null));

        waitForFragment(NewSessionDialog.TAG, 5000, getCurrentActivity());

//        Thread.sleep(1000);
        onView(withId(R.id.description_edit_text)).check(matches(isDisplayed()));

        onView(withId(R.id.description_text)).check(matches(withText("Enter a description")));
        onView(withId(R.id.collection_time_selector)).check(matches(isDisplayed()));
        onView(withId(R.id.new_sess_submit_button)).perform(new ClickAction(Tap.SINGLE, GeneralLocation.CENTER, Press.FINGER, null));
        onView(withId(R.id.export_button)).check(matches(isDisplayed()));

    }

    @Test
    public void openCloseAddToSessionDialog() throws InterruptedException {
//        closeSoftKeyboard();
//        Thread.sleep(1000);
        onView(withId(R.id.add_to_session_button)).perform(new ClickAction(Tap.SINGLE, GeneralLocation.CENTER, Press.FINGER, null));
        waitForFragment(AddSessionDialog.TAG, 5000, getCurrentActivity());

//        Thread.sleep(1000);
        onView(withId(R.id.session_selector)).check(matches(isDisplayed()));

        onView(withId(R.id.collection_time_selector2)).check(matches(isDisplayed()));
        onView(withId(R.id.add_sess_submit_button)).perform(new ClickAction(Tap.SINGLE, GeneralLocation.CENTER, Press.FINGER, null));
        onView(withId(R.id.export_button)).check(matches(isDisplayed()));

    }
}
