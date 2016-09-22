package edu.rose_hulman.nswccrane.dataacquisition;

import android.content.Context;
import android.support.annotation.NonNull;
import android.support.test.espresso.action.ViewActions;
import android.support.test.espresso.matcher.ViewMatchers;
// import android.support.test.espresso.assertion.ViewAssertions;
import android.support.test.runner.AndroidJUnit4;
import android.widget.Button;

// import org.junit.Before;
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
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;
import sqlite.MotionCollectionDBHelper;

import static android.support.test.espresso.Espresso.onView;

@RunWith(AndroidJUnit4.class)
public class ApplicationTest extends JUnitTestCase<MainActivity> {

    public ApplicationTest() {
        super(MainActivity.class);
    }

    class FakePool implements ExecutorService {

        public boolean errorOnAwait;

        public FakePool(){
            errorOnAwait = false;
        }

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
            if (errorOnAwait){
                throw new InterruptedException("Test throw of and interrupted exception.");
            }
            return !errorOnAwait;
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

    class FakeMotionDB extends MotionCollectionDBHelper {

        public boolean successfullyDeleted;

        public FakeMotionDB(Context context) {
            super(context, new Semaphore(1));
            successfullyDeleted = false;
        }

        @Override
        public long DeleteCurrentAccelData(){
            successfullyDeleted = true;
            return 0;
        }
    }

    @Test
    public void testToggleCollectionTrueNoException() throws NoSuchFieldException, IllegalAccessException {
        MainActivity mainActivity = (MainActivity) this.getCurrentActivity();
        Field startedField = getFieldFromMainActivity("mStarted");
        startedField.set(mainActivity, true);
        Field collectionButtonField = getFieldFromMainActivity("mCollectionButton");
        Field dbField = getFieldFromMainActivity("mMotionCollectionDBHelper");
        dbField.set(mainActivity, new FakeMotionDB(mainActivity));
        Field insertionPoolField = getFieldFromMainActivity("mInsertionThreadPool");
        FakePool newPool = new FakePool();
        newPool.errorOnAwait = false;
        insertionPoolField.set(mainActivity, newPool);
        onView(ViewMatchers.withId(R.id.collection_button)).perform(ViewActions.click());
        Button collectionButton = (Button) collectionButtonField.get(mainActivity);
        boolean started = (boolean) startedField.get(mainActivity);
        FakeMotionDB helper = (FakeMotionDB) dbField.get(mainActivity);
        Assert.assertTrue(collectionButton.isActivated());
        Assert.assertTrue(collectionButton.getText().equals("Start Collection"));
        Assert.assertFalse(started);
        Assert.assertTrue(helper.successfullyDeleted);
    }

    private Field getFieldFromMainActivity(String declarationName) throws NoSuchFieldException {
        Field field = MainActivity.class.getDeclaredField(declarationName);
        if(!field.isAccessible()) {
            field.setAccessible(true);
        }
        return field;
    }
}