package edu.rose_hulman.nswccrane.dataacquisition.interfaces;

/**
 * Created by steve on 9/26/16.
 */

public interface ICollectionCallback {

    void resetCollectionButton();
    void setAccelTextViews(double x, double y, double z);
    void setGyroTextViews(double pitch, double roll, double yaw);
}
