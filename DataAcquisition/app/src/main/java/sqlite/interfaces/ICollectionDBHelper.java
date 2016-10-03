package sqlite.interfaces;

import datamodels.AccelDataModel;
import datamodels.GyroDataModel;

/**
 * Created by steve on 9/26/16.
 */

public interface ICollectionDBHelper {
    /*
    void setStartTime(long startTime);
    void setEndTime(long endTime);
    void getAllTimeframesBetween(long startTime, long endTime);
    long deleteCurrentTimeframeData();
    */

    void pushAccelData();
    void pushGyroData();
    void insertAccelData(AccelDataModel data);
    void insertGyroData(GyroDataModel data);
    long deleteCurrentAccelData();
    long deleteCurrentGyroData();

}
