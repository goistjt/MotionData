package edu.rose_hulman.nswccrane.dataacquisition;

import android.app.Application;
import android.test.ApplicationTestCase;
import android.util.Log;

import org.junit.Assert;
import org.junit.Test;

import datamodels.AccelDataModel;

/**
 * <a href="http://d.android.com/tools/testing/testing_android.html">Testing Fundamentals</a>
 */
public class ApplicationTest extends ApplicationTestCase<Application> {

    public ApplicationTest() {
        super(Application.class);
    }

    @Test
    public void testAccelDataModelConstructor() {
        long currentTime = System.currentTimeMillis();
        double inX = 0.0;
        double inY = 0.0;
        double inZ = 0.0;
        AccelDataModel model = new AccelDataModel(currentTime, inX, inY, inZ);
        Assert.assertEquals(currentTime, model.getTime());
        Assert.assertTrue(inX == model.getX());
        Assert.assertTrue(inY == model.getY());
        Assert.assertTrue(inZ == model.getZ());
    }

    @Test
    public void testCollectionButtonSetup() {
    }
}