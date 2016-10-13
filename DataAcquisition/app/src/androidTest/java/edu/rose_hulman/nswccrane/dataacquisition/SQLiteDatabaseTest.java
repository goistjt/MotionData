package edu.rose_hulman.nswccrane.dataacquisition;

import android.database.Cursor;
import android.database.DatabaseUtils;
import android.support.test.runner.AndroidJUnit4;
import com.google.gson.Gson;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;
import datamodels.AccelDataModel;
import datamodels.GyroDataModel;
import datamodels.SessionModel;
import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.testing_utils.AMainActivityTest;
import sqlite.MotionCollectionDBHelper;

/**
 * Created by steve on 10/10/16.
 */

@RunWith(AndroidJUnit4.class)
public class SQLiteDatabaseTest extends AMainActivityTest {

    @Test
    public void testTimeframeEntry() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        motionDB.setStartTime(0);

        motionDB.setEndTime(0);

        Assert.assertTrue(DatabaseUtils.queryNumEntries(motionDB.getWritableDatabase(), mainActivity.getString(R.string.timeframe_table_name)) == 1);
    }

    @Test
    public void testTimeframeCustomTime() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        motionDB.setStartTime(234);

        motionDB.setEndTime(5678);

        Cursor timeframeCursor = motionDB.getWritableDatabase().rawQuery(mainActivity.getString(R.string.select_all_timeframe), new String[] {});

        Assert.assertTrue(timeframeCursor.getCount() == 1);

        Assert.assertTrue(timeframeCursor.getColumnCount() == 2);

        timeframeCursor.moveToFirst();
        Assert.assertTrue(timeframeCursor.getLong(timeframeCursor.getColumnIndex(mainActivity.getString(R.string.start_time))) == 234 && timeframeCursor.getLong(timeframeCursor.getColumnIndex(mainActivity.getString(R.string.end_time))) == 5678);
    }

    @Test
    public void testGetTimeframesBetween() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        motionDB.setStartTime(234);

        motionDB.setEndTime(5678);

        List<TimeframeDataModel> modelList = motionDB.getAllTimeframesBetween(0, System.currentTimeMillis());

        Assert.assertTrue(modelList.size() == 1);

        Assert.assertTrue(modelList.get(0).getStartTime() == 234 && modelList.get(0).getEndTime() == 5678);
    }

    @Test
    public void testGetTimeframesBetweenNone() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        motionDB.setStartTime(234);

        motionDB.setEndTime(5678);

        List<TimeframeDataModel> modelList = motionDB.getAllTimeframesBetween(5800, System.currentTimeMillis());

        Assert.assertTrue(modelList.size() == 0);
    }

    @Test
    public void testGetTimeframesBetweenMultipleOneInOneOut() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        motionDB.setStartTime(234);

        motionDB.setEndTime(5678);

        motionDB.setStartTime(5800);

        motionDB.setEndTime(6000);

        List<TimeframeDataModel> modelList = motionDB.getAllTimeframesBetween(0, 5700);

        Assert.assertTrue(modelList.size() == 1);

        Assert.assertTrue(modelList.get(0).getStartTime() == 234 && modelList.get(0).getEndTime() == 5678);
    }

    @Test
    public void testGetDataBetweenTimesBasicEach() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        motionDB.insertAccelData(new AccelDataModel(0, 0, 0, 0));
        motionDB.pushAccelData();
        motionDB.insertGyroData(new GyroDataModel(0, 0, 0, 0));
        motionDB.pushGyroData();

        SessionModel model = motionDB.getAllDataBetween(0, System.currentTimeMillis());

        Assert.assertTrue(model.getAccelModels().size() == 1);

        Assert.assertTrue(model.getGyroModels().size() == 1);

        AccelDataModel accelData = model.getAccelModels().get(0);

        GyroDataModel gyroData = model.getGyroModels().get(0);

        Assert.assertTrue(accelData.getX() == 0 && accelData.getY() == 0 && accelData.getZ() == 0);

        Assert.assertTrue(gyroData.getPitch() == 0 && gyroData.getRoll() == 0 && gyroData.getYaw() == 0);
    }

    @Test
    public void testGetDataBetweenTimesNone() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        SessionModel model = motionDB.getAllDataBetween(0, System.currentTimeMillis());

        Assert.assertTrue(model.getAccelModels().size() == 0);

        Assert.assertTrue(model.getGyroModels().size() == 0);
    }

    @Test
    public void testGetDataBetweenTimesMultipleOnlyAccel() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        motionDB.insertAccelData(new AccelDataModel(0, 0, 0, 0));
        motionDB.insertAccelData(new AccelDataModel(1, 1, 1, 1));
        motionDB.pushAccelData();

        SessionModel model = motionDB.getAllDataBetween(0, System.currentTimeMillis());

        Assert.assertTrue(model.getAccelModels().size() == 2);

        Assert.assertTrue(model.getGyroModels().size() == 0);

        AccelDataModel accelData = model.getAccelModels().get(0);

        AccelDataModel accelData2 = model.getAccelModels().get(1);

        Assert.assertTrue(accelData.getX() == 0 && accelData.getY() == 0 && accelData.getZ() == 0);

        Assert.assertTrue(accelData2.getX() == 1 && accelData2.getY() == 1 && accelData2.getZ() == 1);
    }

    @Test
    public void testGetDataBetweenTimesMultipleOnlyGyro() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        motionDB.insertGyroData(new GyroDataModel(1, 5, 7, 12));
        motionDB.insertGyroData(new GyroDataModel(3, 19, 2, 5));
        motionDB.pushGyroData();

        SessionModel model = motionDB.getAllDataBetween(0, System.currentTimeMillis());

        Assert.assertTrue(model.getAccelModels().size() == 0);

        Assert.assertTrue(model.getGyroModels().size() == 2);

        GyroDataModel gyroData = model.getGyroModels().get(0);

        GyroDataModel gyroData2 = model.getGyroModels().get(1);

        Assert.assertTrue(gyroData.getPitch() == 5 && gyroData.getRoll() == 7 && gyroData.getYaw() == 12);

        Assert.assertTrue(gyroData2.getPitch() == 19 && gyroData2.getRoll() == 2 && gyroData2.getYaw() == 5);
    }

    @Test
    public void testJsonOutput() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        List<GyroDataModel> gyroList = new ArrayList<>();
        gyroList.add(new GyroDataModel(1, 5, 7, 12));
        gyroList.add(new GyroDataModel(3, 19, 2, 5));

        List<AccelDataModel> accelList = new ArrayList<>();
        accelList.add(new AccelDataModel(1, 12, 12, 12));
        accelList.add(new AccelDataModel(3, 19, 5, 5));

        motionDB.insertAccelData(accelList.get(0));
        motionDB.insertAccelData(accelList.get(1));
        motionDB.pushAccelData();

        motionDB.insertGyroData(gyroList.get(0));
        motionDB.insertGyroData(gyroList.get(1));
        motionDB.pushGyroData();

        Gson gson = new Gson();
        SessionModel modelAfter = gson.fromJson(motionDB.getAllDataAsJson(0, System.currentTimeMillis()), SessionModel.class);

        Assert.assertTrue(modelAfter.getAccelModels().size() == 2);
        Assert.assertTrue(modelAfter.getGyroModels().size() == 2);
    }

    @Test
    public void testJsonOutputNothingInDB() throws NoSuchFieldException, IllegalAccessException {
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        MotionCollectionDBHelper motionDB = (MotionCollectionDBHelper) dbField.get(mainActivity);

        motionDB.onUpgrade(motionDB.getWritableDatabase(), 0, 0);

        Gson gson = new Gson();
        SessionModel modelAfter = gson.fromJson(motionDB.getAllDataAsJson(0, System.currentTimeMillis()), SessionModel.class);

        Assert.assertTrue(modelAfter.getAccelModels().size() == 0);
        Assert.assertTrue(modelAfter.getGyroModels().size() == 0);
    }
}