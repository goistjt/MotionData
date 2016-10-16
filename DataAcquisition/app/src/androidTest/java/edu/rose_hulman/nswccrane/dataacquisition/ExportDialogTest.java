package edu.rose_hulman.nswccrane.dataacquisition;

import android.support.test.runner.AndroidJUnit4;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;

import static android.support.test.espresso.Espresso.closeSoftKeyboard;
import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.action.ViewActions.click;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.matcher.RootMatchers.isDialog;
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

    @Before
    public void openDialog() {
        onView(withId(R.id.export_button)).perform(click());
    }

    @Test
    public void checkDialogButtons() {
        onView(withId(R.id.new_session_button)).check(matches(withText(R.string.new_session)));
        onView(withId(R.id.add_to_session_button)).check(matches(withText(R.string.add_to_session)));
    }

    @Test
    public void openCloseNewSessionDialog() {
        closeSoftKeyboard();
        onView(withId(R.id.new_session_button)).inRoot(isDialog()).perform(click());
        onView(withId(R.id.description_edit_text)).check(matches(isDisplayed()));
        onView(withId(R.id.description_text)).check(matches(withText("Enter a description")));
        onView(withId(R.id.collection_time_selector)).check(matches(isDisplayed()));
        onView(withId(R.id.new_sess_submit_button)).perform(click());
        onView(withId(R.id.export_button)).check(matches(isDisplayed()));
    }

    @Test
    public void openCloseAddToSessionDialog() {
        closeSoftKeyboard();
        onView(withId(R.id.add_to_session_button)).inRoot(isDialog()).perform(click());
        onView(withId(R.id.session_selector)).check(matches(isDisplayed()));
        onView(withId(R.id.collection_time_selector2)).check(matches(isDisplayed()));
        onView(withId(R.id.add_sess_submit_button)).perform(click());
        onView(withId(R.id.export_button)).check(matches(isDisplayed()));
    }
}
