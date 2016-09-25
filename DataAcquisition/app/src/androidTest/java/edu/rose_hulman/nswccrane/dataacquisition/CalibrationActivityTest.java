package edu.rose_hulman.nswccrane.dataacquisition;

import junit.framework.Assert;

import org.junit.Before;
import org.junit.Test;

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

    @Test
    public void testOnAccelerometerChanged() {
        mActivity.accelerometerChanged(new float[]{1, 1, 1});
        Assert.assertEquals(1, mActivity.max_x_noise);
        Assert.assertEquals(1, mActivity.max_y_noise);
        Assert.assertEquals(1, mActivity.max_z_noise);
        mActivity.accelerometerChanged(new float[]{.5F, .5F, .5F});
        Assert.assertEquals(1, mActivity.max_x_noise);
        Assert.assertEquals(1, mActivity.max_y_noise);
        Assert.assertEquals(1, mActivity.max_z_noise);
        mActivity.accelerometerChanged(new float[]{2.5F, 2.5F, 2.5F});
        Assert.assertEquals(2, mActivity.max_x_noise);
        Assert.assertEquals(2, mActivity.max_y_noise);
        Assert.assertEquals(2, mActivity.max_z_noise);
    }
}
