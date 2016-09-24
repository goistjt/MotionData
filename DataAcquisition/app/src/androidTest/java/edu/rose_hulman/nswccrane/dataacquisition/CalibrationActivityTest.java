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
    public void testInitSensorManager() {
        Assert.assertNotNull(mActivity.getSensorManager());
    }

    @Test
    public void testInitSensors() {
        Assert.assertNotNull(mActivity.getAccelerometer());
        Assert.assertNotNull(mActivity.getGyroscope());
    }

}
