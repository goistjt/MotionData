package edu.rose_hulman.nswccrane.dataacquisition;

/**
 * Created by steve on 9/26/16.
 */

import android.hardware.Sensor;
import android.hardware.SensorManager;
import android.support.annotation.NonNull;
import android.support.test.InstrumentationRegistry;
import android.support.test.espresso.action.ViewActions;
import android.support.test.espresso.assertion.ViewAssertions;
import android.support.test.espresso.matcher.ViewMatchers;
import android.support.test.runner.AndroidJUnit4;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import datamodels.AccelDataModel;
import datamodels.GyroDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;
import sqlite.interfaces.ICollectionDBHelper;
import static android.support.test.espresso.Espresso.onView;
import static android.support.test.espresso.assertion.ViewAssertions.matches;
import static android.support.test.espresso.matcher.ViewMatchers.isEnabled;
import static android.support.test.espresso.matcher.ViewMatchers.withId;

@RunWith(AndroidJUnit4.class)
public class CollectionActivityTests extends JUnitTestCase<MainActivity> {

    private MainActivity mainActivity;

    public CollectionActivityTests() {
        super(MainActivity.class);
    }

    class FakeExecutorService implements ExecutorService {

        boolean shutdownOccurred = false;
        boolean terminationOccurred = true;

        @Override
        public void shutdown() {
            shutdownOccurred = true;
        }

        @NonNull
        @Override
        public List<Runnable> shutdownNow() {
            shutdownOccurred = true;
            return new ArrayList<>();
        }

        @Override
        public boolean isShutdown() {
            return shutdownOccurred;
        }

        @Override
        public boolean isTerminated() {
            return terminationOccurred;
        }

        @Override
        public boolean awaitTermination(long timeout, @NonNull TimeUnit unit) throws InterruptedException {
            terminationOccurred = true;
            return true;
        }

        @NonNull
        @Override
        public <T> Future<T> submit(@NonNull Callable<T> task) {
            return null;
        }

        @NonNull
        @Override
        public <T> Future<T> submit(@NonNull Runnable task, T result) {
            return null;
        }

        @NonNull
        @Override
        public Future<?> submit(@NonNull Runnable task) {
            return null;
        }

        @NonNull
        @Override
        public <T> List<Future<T>> invokeAll(@NonNull Collection<? extends Callable<T>> tasks) throws InterruptedException {
            return null;
        }

        @NonNull
        @Override
        public <T> List<Future<T>> invokeAll(@NonNull Collection<? extends Callable<T>> tasks, long timeout, @NonNull TimeUnit unit) throws InterruptedException {
            return null;
        }

        @NonNull
        @Override
        public <T> T invokeAny(@NonNull Collection<? extends Callable<T>> tasks) throws InterruptedException, ExecutionException {
            return null;
        }

        @Override
        public <T> T invokeAny(@NonNull Collection<? extends Callable<T>> tasks, long timeout, @NonNull TimeUnit unit) throws InterruptedException, ExecutionException, TimeoutException {
            return null;
        }

        @Override
        public void execute(@NonNull Runnable command) {

        }
    }

    class FakeCollectionDB implements ICollectionDBHelper {

        boolean pushAccelDataHit = false;
        boolean pushGyroDataHit = false;
        boolean insertAccelDataHit = false;
        boolean insertGyroDataHit = false;
        boolean deleteCurrentAccelDataHit = false;
        boolean deleteCurrentGyroDataHit = false;

        public FakeCollectionDB() {
        }

        /*
        @Override
        public void setStartTime(long startTime) {
        }

        @Override
        public void setEndTime(long endTime) {
        }

        @Override
        public void getAllTimeframesBetween(long startTime, long endTime) {
        }

        @Override
        public long deleteCurrentTimeframeData() {
            return 0;
        }
        */

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

    @Before
    public void before() {
        mainActivity = (MainActivity) getCurrentActivity();
    }

    @Test
    public void testToggleCollectionTrue() throws NoSuchFieldException, IllegalAccessException, InterruptedException {

        Field startedField = getFieldFromMainActivity("mStarted");
        startedField.set(mainActivity, true);

        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        dbField.set(mainActivity, new FakeCollectionDB());

        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");

        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");

        onView(ViewMatchers.withId(R.id.collection_button)).perform(ViewActions.click());

        ExecutorService collectionService = (ExecutorService) collectionServiceField.get(mainActivity);
        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);

        collectionService.shutdown();
        collectionService.awaitTermination(30, TimeUnit.SECONDS);

        toggleService.shutdown();
        toggleService.awaitTermination(30, TimeUnit.SECONDS);

        onView(withId(R.id.collection_button)).check(matches(isEnabled()));
        onView(withId(R.id.collection_button)).check(matches(ViewMatchers.withText(mainActivity.getString(R.string.collect_data))));

        boolean started = (boolean) startedField.get(mainActivity);
        Assert.assertFalse(started);

        FakeCollectionDB helper = (FakeCollectionDB) dbField.get(mainActivity);
        Assert.assertTrue(helper.pushAccelDataHit);
        Assert.assertTrue(helper.pushGyroDataHit);
    }

    @Test
    public void testToggleCollectionFalse() throws NoSuchFieldException, IllegalAccessException, InterruptedException {

        Field startedField = getFieldFromMainActivity("mStarted");
        startedField.set(mainActivity, false);

        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        dbField.set(mainActivity, new FakeCollectionDB());

        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");
        collectionServiceField.set(mainActivity, new FakeExecutorService());

        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");
        toggleServiceField.set(mainActivity, new FakeExecutorService());

        onView(ViewMatchers.withId(R.id.collection_button)).perform(ViewActions.click());

        ExecutorService collectionService = (ExecutorService) collectionServiceField.get(mainActivity);
        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);

        collectionService.shutdown();
        collectionService.awaitTermination(30, TimeUnit.SECONDS);

        toggleService.shutdown();
        toggleService.awaitTermination(30, TimeUnit.SECONDS);

        boolean started = (boolean) startedField.get(mainActivity);
        Assert.assertTrue(started);

        onView(withId(R.id.collection_button)).check(matches(isEnabled()));
        onView(withId(R.id.collection_button)).check(matches(ViewMatchers.withText(mainActivity.getString(R.string.stop_collection))));
    }

    @Test
    public void testPopulateSensorDependencies() throws NoSuchFieldException, IllegalAccessException, InterruptedException {

        Field startedField = getFieldFromMainActivity("mStarted");

        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");

        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");
        collectionServiceField.set(mainActivity, new FakeExecutorService());

        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");
        toggleServiceField.set(mainActivity, new FakeExecutorService());

        Field SensorManagerField = getFieldFromMainActivity("mSensorManager");

        Field AccelerometerField = getFieldFromMainActivity("mAccelerometer");

        mainActivity.populateSensorDependencies();

        boolean started = (boolean) startedField.get(mainActivity);
        Assert.assertFalse(started);

        ICollectionDBHelper dbHelper = (ICollectionDBHelper) dbField.get(mainActivity);
        Assert.assertTrue(dbHelper.getClass().getInterfaces()[0].equals(ICollectionDBHelper.class));

        ExecutorService collectService = (ExecutorService) collectionServiceField.get(mainActivity);
        Assert.assertTrue(!collectService.isTerminated() && !collectService.isShutdown());

        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);
        Assert.assertTrue(!toggleService.isTerminated() && !toggleService.isShutdown());

        Sensor accelerometer = (Sensor) AccelerometerField.get(mainActivity);
        Assert.assertTrue(accelerometer.getType() == Sensor.TYPE_ACCELEROMETER);

        SensorManager sensorManager = (SensorManager) SensorManagerField.get(mainActivity);
        Assert.assertTrue(sensorManager.getSensorList(Sensor.TYPE_ACCELEROMETER).contains(accelerometer));
    }

    @Test
    public void testTeardownSensorDependencies() throws NoSuchFieldException, InterruptedException, IllegalAccessException {

        Field startedField = getFieldFromMainActivity("mStarted");
        startedField.set(mainActivity, true);

        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        dbField.set(mainActivity, new FakeCollectionDB());

        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");
        collectionServiceField.set(mainActivity, new FakeExecutorService());

        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");
        toggleServiceField.set(mainActivity, new FakeExecutorService());

        mainActivity.teardownSensorDependencies();

        boolean startedVal = (boolean) startedField.get(mainActivity);
        Assert.assertTrue(!startedVal);

        FakeExecutorService toggleServiceVal = (FakeExecutorService) toggleServiceField.get(mainActivity);
        Assert.assertTrue(toggleServiceVal.isTerminated() && toggleServiceVal.isShutdown());

        FakeExecutorService collectionServiceVal = (FakeExecutorService) collectionServiceField.get(mainActivity);
        Assert.assertTrue(collectionServiceVal.isTerminated() && collectionServiceVal.isShutdown());
    }

    @Test
    public void testAccelerometerChangedZeros() throws NoSuchFieldException, IllegalAccessException, InterruptedException {

        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        dbField.set(mainActivity, new FakeCollectionDB());

        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");

        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");

        final AccelDataModel dataModel = new AccelDataModel(0, 0, 0, 0);

        InstrumentationRegistry.getInstrumentation().runOnMainSync(new Runnable() {
            @Override
            public void run() {
                mainActivity.accelerometerChanged(dataModel);
            }
        });

        ExecutorService collectionService = (ExecutorService) collectionServiceField.get(mainActivity);
        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);

        collectionService.shutdown();
        collectionService.awaitTermination(30, TimeUnit.SECONDS);

        toggleService.shutdown();
        toggleService.awaitTermination(30, TimeUnit.SECONDS);

        FakeCollectionDB fakeDB = (FakeCollectionDB) dbField.get(mainActivity);
        Assert.assertTrue(fakeDB.insertAccelDataHit);

        onView(ViewMatchers.withId(R.id.x_accel_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("X: 0.000000 m/s²")));
        onView(ViewMatchers.withId(R.id.y_accel_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Y: 0.000000 m/s²")));
        onView(ViewMatchers.withId(R.id.z_accel_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Z: 0.000000 m/s²")));
    }

    @Test
    public void testAccelerometerChangedVarious() throws NoSuchFieldException, IllegalAccessException, InterruptedException {

        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        dbField.set(mainActivity, new FakeCollectionDB());

        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");

        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");

        final AccelDataModel dataModel = new AccelDataModel(0, -1.23, 4.56, 5.000000001);


        InstrumentationRegistry.getInstrumentation().runOnMainSync(new Runnable() {
            @Override
            public void run() {
                mainActivity.accelerometerChanged(dataModel);
            }
        });

        ExecutorService collectionService = (ExecutorService) collectionServiceField.get(mainActivity);
        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);

        collectionService.shutdown();
        collectionService.awaitTermination(30, TimeUnit.SECONDS);

        toggleService.shutdown();
        toggleService.awaitTermination(30, TimeUnit.SECONDS);

        FakeCollectionDB fakeDB = (FakeCollectionDB) dbField.get(mainActivity);
        Assert.assertTrue(fakeDB.insertAccelDataHit);

        onView(ViewMatchers.withId(R.id.x_accel_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("X: -1.230000 m/s²")));
        onView(ViewMatchers.withId(R.id.y_accel_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Y: 4.560000 m/s²")));
        onView(ViewMatchers.withId(R.id.z_accel_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Z: 5.000000 m/s²")));
    }

    @Test
    public void testGyroscopeChangedZeros() throws NoSuchFieldException, IllegalAccessException, InterruptedException {

        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        dbField.set(mainActivity, new FakeCollectionDB());

        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");

        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");

        final GyroDataModel dataModel = new GyroDataModel(0, 0, 0, 0);

        InstrumentationRegistry.getInstrumentation().runOnMainSync(new Runnable() {
            @Override
            public void run() {
                mainActivity.gyroscopeChanged(dataModel);
            }
        });

        ExecutorService collectionService = (ExecutorService) collectionServiceField.get(mainActivity);
        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);

        collectionService.shutdown();
        collectionService.awaitTermination(30, TimeUnit.SECONDS);

        toggleService.shutdown();
        toggleService.awaitTermination(30, TimeUnit.SECONDS);

        FakeCollectionDB fakeDB = (FakeCollectionDB) dbField.get(mainActivity);
        Assert.assertTrue(fakeDB.insertGyroDataHit);

        onView(ViewMatchers.withId(R.id.pitch_gyro_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Pitch: 0.000000\u00b0")));
        onView(ViewMatchers.withId(R.id.roll_gyro_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Roll: 0.000000\u00b0")));
        onView(ViewMatchers.withId(R.id.yaw_gyro_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Yaw: 0.000000\u00b0")));
    }

    @Test
    public void testGyroscopeChangedVarious() throws NoSuchFieldException, IllegalAccessException, InterruptedException {

        Field dbField = getFieldFromMainActivity("mCollectionDBHelper");
        dbField.set(mainActivity, new FakeCollectionDB());

        Field collectionServiceField = getFieldFromMainActivity("mCollectionService");

        Field toggleServiceField = getFieldFromMainActivity("mToggleButtonService");

        final GyroDataModel dataModel = new GyroDataModel(0, -1.23, 4.56, 5.000000001);

        InstrumentationRegistry.getInstrumentation().runOnMainSync(new Runnable() {
            @Override
            public void run() {
                mainActivity.gyroscopeChanged(dataModel);
            }
        });

        ExecutorService collectionService = (ExecutorService) collectionServiceField.get(mainActivity);
        ExecutorService toggleService = (ExecutorService) toggleServiceField.get(mainActivity);

        collectionService.shutdown();
        collectionService.awaitTermination(30, TimeUnit.SECONDS);

        toggleService.shutdown();
        toggleService.awaitTermination(30, TimeUnit.SECONDS);

        FakeCollectionDB fakeDB = (FakeCollectionDB) dbField.get(mainActivity);
        Assert.assertTrue(fakeDB.insertGyroDataHit);

        onView(ViewMatchers.withId(R.id.pitch_gyro_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Pitch: -1.230000\u00b0")));
        onView(ViewMatchers.withId(R.id.roll_gyro_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Roll: 4.560000\u00b0")));
        onView(ViewMatchers.withId(R.id.yaw_gyro_text_view)).check(ViewAssertions.matches(ViewMatchers.withText("Yaw: 5.000000\u00b0")));
    }


    @Test
    public void testUISetup() throws NoSuchFieldException, IllegalAccessException, InterruptedException, NoSuchMethodException, InvocationTargetException {

        final Method setupMethod = getMethodFromMainActivity("setupUIElements");
        InstrumentationRegistry.getInstrumentation().runOnMainSync(new Runnable() {
            @Override
            public void run() {
                try {
                    setupMethod.invoke(mainActivity);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });

        onView(ViewMatchers.withId(R.id.pitch_gyro_text_view)).check(ViewAssertions.matches(ViewMatchers.withText(mainActivity.getString(R.string.pitch_gyro_default))));
        onView(ViewMatchers.withId(R.id.roll_gyro_text_view)).check(ViewAssertions.matches(ViewMatchers.withText(mainActivity.getString(R.string.roll_gyro_default))));
        onView(ViewMatchers.withId(R.id.yaw_gyro_text_view)).check(ViewAssertions.matches(ViewMatchers.withText(mainActivity.getString(R.string.yaw_gyro_default))));

        onView(ViewMatchers.withId(R.id.x_accel_text_view)).check(ViewAssertions.matches(ViewMatchers.withText(mainActivity.getString(R.string.x_accel_default))));
        onView(ViewMatchers.withId(R.id.y_accel_text_view)).check(ViewAssertions.matches(ViewMatchers.withText(mainActivity.getString(R.string.y_accel_default))));
        onView(ViewMatchers.withId(R.id.z_accel_text_view)).check(ViewAssertions.matches(ViewMatchers.withText(mainActivity.getString(R.string.z_accel_default))));

        onView(withId(R.id.collection_button)).check(matches(isEnabled()));
        onView(withId(R.id.collection_button)).check(matches(ViewMatchers.withText(mainActivity.getString(R.string.collect_data))));
    }

    private Field getFieldFromMainActivity(String declarationName) throws NoSuchFieldException {
        Field field = MainActivity.class.getDeclaredField(declarationName);
        if (!field.isAccessible()) {
            field.setAccessible(true);
        }
        return field;
    }

    private Method getMethodFromMainActivity(String declarationName) throws NoSuchMethodException {
        Method method = MainActivity.class.getDeclaredMethod(declarationName);
        if (!method.isAccessible()) {
            method.setAccessible(true);
        }
        return method;
    }
}