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
import org.junit.Test;
import org.junit.runner.RunWith;
import java.lang.reflect.Field;
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

    public CollectionActivityTests() {
        super(MainActivity.class);
    }

    class FakeExecutorService implements ExecutorService {

        public boolean shutdownOccurred = false;
        public boolean terminationOccurred = true;

        @Override
        public void shutdown() {
            shutdownOccurred = true;
        }

        @NonNull
        @Override
        public List<Runnable> shutdownNow() {
            shutdownOccurred = true;
            return null;
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
        public boolean awaitTermination(long timeout, TimeUnit unit) throws InterruptedException {
            terminationOccurred = true;
            return terminationOccurred;
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

        public boolean pushAccelDataHit = false;
        public boolean pushGyroDataHit = false;
        public boolean insertAccelDataHit = false;
        public boolean insertGyroDataHit = false;
        public boolean deleteCurrentAccelDataHit = false;
        public boolean deleteCurrentGyroDataHit = false;

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
        onView(withId(R.id.collection_button)).check(matches(ViewMatchers.withText(mainActivity.getString(R.string.StartCollection))));

        boolean started = (boolean) startedField.get(mainActivity);
        Assert.assertFalse(started);

        FakeCollectionDB helper = (FakeCollectionDB) dbField.get(mainActivity);
        Assert.assertTrue(helper.pushAccelDataHit);
        Assert.assertTrue(helper.pushGyroDataHit);
    }

    @Test
    public void testToggleCollectionFalse() throws NoSuchFieldException, IllegalAccessException, InterruptedException {
        MainActivity mainActivity = (MainActivity) this.getCurrentActivity();

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
        onView(withId(R.id.collection_button)).check(matches(ViewMatchers.withText(mainActivity.getString(R.string.StopCollection))));
    }

    @Test
    public void testPopulateSensorDependencies() throws NoSuchFieldException, IllegalAccessException, InterruptedException {
        final MainActivity mainActivity = (MainActivity) this.getCurrentActivity();

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
        final MainActivity mainActivity = (MainActivity) this.getCurrentActivity();

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
        final MainActivity mainActivity = (MainActivity) this.getCurrentActivity();

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
        final MainActivity mainActivity = (MainActivity) this.getCurrentActivity();

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
        final MainActivity mainActivity = (MainActivity) this.getCurrentActivity();

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
        final MainActivity mainActivity = (MainActivity) this.getCurrentActivity();

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

    private Field getFieldFromMainActivity(String declarationName) throws NoSuchFieldException {
        Field field = MainActivity.class.getDeclaredField(declarationName);
        if (!field.isAccessible()) {
            field.setAccessible(true);
        }
        return field;
    }
}