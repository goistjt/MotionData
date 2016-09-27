package edu.rose_hulman.nswccrane.dataacquisition.interfaces;

/**
 * Created by steve on 9/21/16.
 */

public interface ICollectionActivity {

    void populateSensorDependencies();

    void teardownSensorDependencies();

    void toggleCollection();
}
