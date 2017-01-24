package edu.rose_hulman.nswccrane.dataacquisition;

import junit.framework.Assert;

import org.androidannotations.annotations.IgnoreWhen;
import org.junit.Before;
import org.junit.Ignore;
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

    @Ignore
    @Test
    public void testOnAccelerometerChanged() {
        mActivity.accelerometerChanged(new float[]{1, 1, 1});
        Assert.assertEquals(1F, mActivity.max_x_noise);
        Assert.assertEquals(1F, mActivity.max_y_noise);
        Assert.assertEquals(1F, mActivity.max_z_noise);
        mActivity.accelerometerChanged(new float[]{.5F, .5F, .5F});
        Assert.assertEquals(1F, mActivity.max_x_noise);
        Assert.assertEquals(1F, mActivity.max_y_noise);
        Assert.assertEquals(1F, mActivity.max_z_noise);
        mActivity.accelerometerChanged(new float[]{2.5F, 2.5F, 2.5F});
        Assert.assertEquals(2F, mActivity.max_x_noise);
        Assert.assertEquals(2F, mActivity.max_y_noise);
        Assert.assertEquals(2F, mActivity.max_z_noise);
    }

    @Test
    public void testOnGyroscopeChanged() {
        mActivity.gyroscopeChanged(new float[]{1, 1, 1});
        Assert.assertEquals(1F, mActivity.max_roll_noise);
        Assert.assertEquals(1F, mActivity.max_pitch_noise);
        Assert.assertEquals(1F, mActivity.max_yaw_noise);
        mActivity.gyroscopeChanged(new float[]{.5F, .5F, .5F});
        Assert.assertEquals(1F, mActivity.max_roll_noise);
        Assert.assertEquals(1F, mActivity.max_pitch_noise);
        Assert.assertEquals(1F, mActivity.max_yaw_noise);
        mActivity.gyroscopeChanged(new float[]{2.5F, 2.5F, 2.5F});
        Assert.assertEquals(2F, mActivity.max_roll_noise);
        Assert.assertEquals(2F, mActivity.max_pitch_noise);
        Assert.assertEquals(2F, mActivity.max_yaw_noise);
    }
}
