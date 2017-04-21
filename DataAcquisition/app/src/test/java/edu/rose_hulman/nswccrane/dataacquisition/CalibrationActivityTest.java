package edu.rose_hulman.nswccrane.dataacquisition;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * Created by Jeremiah Goist on 9/24/2016.
 */

@Ignore
public class CalibrationActivityTest {
    private CalibrationActivity mActivity;

    @Before
    public void getActivity() {
        mActivity = new CalibrationActivity();
    }

    @Test
    public void testOnAccelerometerChanged() {
        mActivity.initDegreeLists();
        mActivity.accelerometerChanged(new float[]{1, 1, 1});
        mActivity.accelerometerChanged(new float[]{.5F, .5F, .5F});
        assertEquals(.75F, mActivity.calculateAverage(mActivity.xVals), .0);
    }

    @Test
    public void testOnGyroscopeChanged() {
        mActivity.initDegreeLists();
        mActivity.gyroscopeChanged(new float[]{1, 1, 1});
        mActivity.gyroscopeChanged(new float[]{.5F, .5F, .5F});
        assertEquals(.75F, mActivity.calculateAverage(mActivity.rollVals), .0);
    }
}
