package edu.rose_hulman.nswccrane.dataacquisition;

/**
 * Created by steve on 9/26/16.
 */

import android.hardware.Sensor;
import android.hardware.SensorManager;
import android.support.annotation.NonNull;
import android.support.test.espresso.action.ViewActions;
import android.support.test.espresso.matcher.ViewMatchers;
import android.support.test.runner.AndroidJUnit4;
import android.widget.Button;
import android.widget.TextView;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.lang.reflect.Field;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import datamodels.AccelDataModel;
import datamodels.GyroDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;
import sqlite.interfaces.ICollectionDBHelper;

import static android.support.test.espresso.Espresso.onView;

@RunWith(AndroidJUnit4.class)
public class CollectionActivityTests extends JUnitTestCase<MainActivity> {

    public CollectionActivityTests() {
        super(MainActivity.class);
    }

    class FakeExecutorService implements ExecutorService {

        @Override
        public void shutdown() {

        }

        @NonNull
        @Override
        public List<Runnable> shutdownNow() {
            return null;
        }

        @Override
        public boolean isShutdown() {
            return false;
        }

        @Override
        public boolean isTerminated() {
            return false;
        }

        @Override
        public boolean awaitTermination(long timeout, TimeUnit unit) throws InterruptedException {
            return false;
        }

        @NonNull
        @Override
        public <T> Future<T> submit(Callable<T> task) {
            return null;
        }

        @NonNull
        @Override
        public <T> Future<T> submit(Runnable task, T result) {
            return null;
        }

        @NonNull
        @Override
        public Future<?> submit(Runnable task) {
            return null;
        }

        @NonNull
        @Override
        public <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks) throws InterruptedException {
            return null;
        }

        @NonNull
        @Override
        public <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks, long timeout, TimeUnit unit) throws InterruptedException {
            return null;
        }

        @NonNull
        @Override
        public <T> T invokeAny(Collection<? extends Callable<T>> tasks) throws InterruptedException, ExecutionException {
            return null;
        }

        @Override
        public <T> T invokeAny(Collection<? extends Callable<T>> tasks, long timeout, TimeUnit unit) throws InterruptedException, ExecutionException, TimeoutException {
            return null;
        }

        @Override
        public void execute(Runnable command) {

        }
    }

    class FakeCollectionDB implements ICollectionDBHelper {

        public boolean pushAccelDataHit;
        public boolean pushGyroDataHit;
        public boolean insertAccelDataHit;
        public boolean insertGyroDataHit;
        public boolean deleteCurrentAccelDataHit;
        public boolean deleteCurrentGyroDataHit;

        public FakeCollectionDB() {
        }

        @Override
        public void pushAccelData() {
            pushAccelDataHit = true;
        }

        @Override
        public void pushGyroData() {
            pushGyroDataHit = true;
        }

        @Override
        public void insertAccelData(AccelDataModel data) {
            insertAccelDataHit = true;
        }

        @Override
        public void insertGyroData(GyroDataModel data) {
            insertGyroDataHit = true;
        }

        @Override
        public long deleteCurrentAccelData() {
            deleteCurrentAccelDataHit = true;
            return 0;
        }

        @Override
        public long deleteCurrentGyroData() {
            deleteCurrentGyroDataHit = true;
            return 0;
        }
    }

    @Test
    public void testToggleCollectionTrue() throws NoSuchFieldException, IllegalAccessException, InterruptedException {
        MainActivity mainActivity = (MainActivity) this.getCurrentActivity();
        Field startedField = getFieldFromMainActivity("mStarted");
        Field collectionButtonField = getFieldFromMainActivity("mCollectionButton");
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        dbField.set(mainActivity, new FakeCollectionDB());
        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");
        collectionServiceField.set(mainActivity, new FakeExecutorService());
        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");
        startedField.set(mainActivity, true);
        onView(ViewMatchers.withId(R.id.collection_button)).perform(ViewActions.click());
        Button collectionButton = (Button) collectionButtonField.get(mainActivity);
        boolean started = (boolean) startedField.get(mainActivity);
        FakeCollectionDB helper = (FakeCollectionDB) dbField.get(mainActivity);
        ExecutorService execService = (ExecutorService) collectionServiceField.get(mainActivity);
        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);
        execService.shutdown();
        execService.awaitTermination(30, TimeUnit.SECONDS);
        toggleService.shutdown();
        toggleService.awaitTermination(30, TimeUnit.SECONDS);
        Assert.assertTrue(collectionButton.isActivated());
        Assert.assertTrue(collectionButton.getText().equals(mainActivity.getString(R.string.StartCollection)));
        Assert.assertFalse(started);
        Assert.assertTrue(helper.pushAccelDataHit);
        Assert.assertTrue(helper.pushGyroDataHit);
    }

    @Test
    public void testToggleCollectionFalse() throws NoSuchFieldException, IllegalAccessException, InterruptedException {
        MainActivity mainActivity = (MainActivity) this.getCurrentActivity();
        Field startedField = getFieldFromMainActivity("mStarted");
        startedField.set(mainActivity, false);
        Field collectionButtonField = getFieldFromMainActivity("mCollectionButton");
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        dbField.set(mainActivity, new FakeCollectionDB());
        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");
        collectionServiceField.set(mainActivity, new FakeExecutorService());
        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");
        onView(ViewMatchers.withId(R.id.collection_button)).perform(ViewActions.click());
        Button collectionButton = (Button) collectionButtonField.get(mainActivity);
        boolean started = (boolean) startedField.get(mainActivity);
        ExecutorService execService = (ExecutorService) collectionServiceField.get(mainActivity);
        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);
        execService.shutdown();
        execService.awaitTermination(30, TimeUnit.SECONDS);
        toggleService.shutdown();
        toggleService.awaitTermination(30, TimeUnit.SECONDS);
        Assert.assertTrue(collectionButton.isActivated());
        Assert.assertTrue(collectionButton.getText().equals(mainActivity.getString(R.string.StopCollection)));
        Assert.assertTrue(started);
    }

    @Test
    public void testPopulateSensorDependencies() throws NoSuchFieldException, IllegalAccessException {
        MainActivity mainActivity = (MainActivity) this.getCurrentActivity();
        Field startedField = getFieldFromMainActivity("mStarted");
        Field collectionButtonField = getFieldFromMainActivity("mCollectionButton");
        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");
        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");
        Field XTextViewField = getFieldFromMainActivity("mXTextView");
        Field YTextViewField = getFieldFromMainActivity("mYTextView");
        Field ZTextViewField = getFieldFromMainActivity("mZTextView");
        Field PitchTextViewField = getFieldFromMainActivity("mPitchTextView");
        Field RollTextViewField = getFieldFromMainActivity("mRollTextView");
        Field YawTextViewField = getFieldFromMainActivity("mYawTextView");
        Field SensorManagerField = getFieldFromMainActivity("mSensorManager");
        Field AccelerometerField = getFieldFromMainActivity("mAccelerometer");
        Field GyroscopeField = getFieldFromMainActivity("mGyroscope");
        mainActivity.populateSensorDependencies();
        boolean started = (boolean) startedField.get(mainActivity);
        Assert.assertFalse(started);
        Button collectionButton = (Button) collectionButtonField.get(mainActivity);
        Assert.assertTrue(collectionButton.getText().equals(mainActivity.getString(R.string.StartCollection)));
        ICollectionDBHelper dbHelper = (ICollectionDBHelper) dbField.get(mainActivity);
        Class[] classArray = new Class[1];
        classArray[0] = ICollectionDBHelper.class;
        Assert.assertTrue(dbHelper.getClass().getInterfaces().equals(classArray));
        ExecutorService collectService = (ExecutorService) collectionServiceField.get(mainActivity);
        Assert.assertTrue(!collectService.isTerminated() && !collectService.isShutdown());
        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);
        Assert.assertTrue(!toggleService.isTerminated() && !toggleService.isShutdown());
        TextView xTextView = (TextView) XTextViewField.get(mainActivity);
        Assert.assertTrue(xTextView.getText().equals(mainActivity.getString(R.string.x_accel_default)));
        TextView yTextView = (TextView) YTextViewField.get(mainActivity);
        Assert.assertTrue(yTextView.getText().equals(mainActivity.getString(R.string.y_accel_default)));
        TextView zTextView = (TextView) ZTextViewField.get(mainActivity);
        Assert.assertTrue(zTextView.getText().equals(mainActivity.getString(R.string.z_accel_default)));
        TextView pitchTextView = (TextView) PitchTextViewField.get(mainActivity);
        Assert.assertTrue(pitchTextView.getText().equals(mainActivity.getString(R.string.pitch_gyro_default)));
        TextView rollTextView = (TextView) RollTextViewField.get(mainActivity);
        Assert.assertTrue(rollTextView.getText().equals(mainActivity.getString(R.string.roll_gyro_default)));
        TextView yawTextView = (TextView) YawTextViewField.get(mainActivity);
        Assert.assertTrue(yawTextView.getText().equals(mainActivity.getString(R.string.yaw_gyro_default)));
        Sensor accelerometer = (Sensor) AccelerometerField.get(mainActivity);
        Assert.assertTrue(accelerometer.getType() == Sensor.TYPE_ACCELEROMETER);
        Sensor gyroscope = (Sensor) GyroscopeField.get(mainActivity);
        Assert.assertTrue(gyroscope.getName().equals(Sensor.TYPE_GYROSCOPE));
        SensorManager sensorManager = (SensorManager) SensorManagerField.get(mainActivity);
        Assert.assertTrue(sensorManager.getSensorList(Sensor.TYPE_ACCELEROMETER).contains(accelerometer) && sensorManager.getSensorList(Sensor.TYPE_GYROSCOPE).contains(gyroscope));
    }

    private Field getFieldFromMainActivity(String declarationName) throws NoSuchFieldException {
        Field field = MainActivity.class.getDeclaredField(declarationName);
        if (!field.isAccessible()) {
            field.setAccessible(true);
        }
        return field;
    }
}