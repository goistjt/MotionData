package edu.rose_hulman.nswccrane.dataacquisition.interfaces;

import datamodels.AccelDataModel;
import datamodels.GyroDataModel;

/**
 * Created by steve on 9/21/16.
 */

public interface ICollectionActivity {

    void populateSensorDependencies();

    void teardownSensorDependencies();

    void toggleCollection();

    void accelerometerChanged(AccelDataModel dataModel);

    void gyroscopeChanged(GyroDataModel dataModel);
}
