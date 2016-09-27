package sqlite.interfaces;

import datamodels.AccelDataModel;
import datamodels.GyroDataModel;

/**
 * Created by steve on 9/26/16.
 */

public interface ICollectionDBHelper {

    void pushAccelData();
    void pushGyroData();
    void insertAccelData(AccelDataModel data);
    void insertGyroData(GyroDataModel data);
    long deleteCurrentAccelData();
    long deleteCurrentGyroData();
}
