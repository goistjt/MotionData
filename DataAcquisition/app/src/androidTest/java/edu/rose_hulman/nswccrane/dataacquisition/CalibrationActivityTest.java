package edu.rose_hulman.nswccrane.dataacquisition;

import org.junit.Before;

import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;

/**
 * Created by Jeremiah Goist on 9/24/2016.
 */

public class CalibrationActivityTest extends JUnitTestCase<CalibrationActivity> {
    private CalibrationActivity mActivity;

    public CalibrationActivityTest() {
        super(CalibrationActivity.class);
    }

    @Before
    public void getActivity() {
        mActivity = (CalibrationActivity) getCurrentActivity();
    }

}
