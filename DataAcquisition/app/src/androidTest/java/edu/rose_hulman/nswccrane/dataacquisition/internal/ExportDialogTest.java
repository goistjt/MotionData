package edu.rose_hulman.nswccrane.dataacquisition.internal;

import android.support.test.runner.AndroidJUnit4;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import edu.rose_hulman.nswccrane.dataacquisition.MainActivity;
import edu.rose_hulman.nswccrane.dataacquisition.R;

import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.action.ViewActions.click;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
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
        onView(withId(android.R.id.button1)).check(matches(withText(R.string.new_session)));
        onView(withId(android.R.id.button2)).check(matches(withText(R.string.add_to_session)));
    }

    @Test
    public void nothing() {

    }
}
