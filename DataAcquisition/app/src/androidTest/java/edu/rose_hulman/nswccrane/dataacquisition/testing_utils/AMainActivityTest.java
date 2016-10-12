package edu.rose_hulman.nswccrane.dataacquisition.testing_utils;

import android.support.test.runner.AndroidJUnit4;

import org.junit.Before;
import org.junit.runner.RunWith;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

import edu.rose_hulman.nswccrane.dataacquisition.MainActivity;
import edu.rose_hulman.nswccrane.dataacquisition.internal.JUnitTestCase;

/**
 * Created by steve on 10/12/16.
 */

@RunWith(AndroidJUnit4.class)
public abstract class AMainActivityTest extends JUnitTestCase<MainActivity> {

    protected MainActivity mainActivity;

    public AMainActivityTest() {
        super(MainActivity.class);
    }

    @Before
    public void before() {
        mainActivity = (MainActivity) getCurrentActivity();
    }

    protected Field getFieldFromMainActivity(String declarationName) throws NoSuchFieldException {
        Field field = MainActivity.class.getDeclaredField(declarationName);
        if (!field.isAccessible()) {
            field.setAccessible(true);
        }
        return field;
    }

    protected Method getMethodFromMainActivity(String declarationName) throws NoSuchMethodException {
        Method method = MainActivity.class.getDeclaredMethod(declarationName);
        if (!method.isAccessible()) {
            method.setAccessible(true);
        }
        return method;
    }
}
