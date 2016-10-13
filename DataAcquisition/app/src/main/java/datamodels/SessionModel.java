package datamodels;

import java.util.List;

/**
 * Created by steve on 10/10/16.
 */

public class SessionModel {

    private List<AccelDataModel> accelModels;
    private List<GyroDataModel> gyroModels;

    public SessionModel(List<AccelDataModel> accels, List<GyroDataModel> gyros) {
        accelModels = accels;
        gyroModels = gyros;
    }

    public List<AccelDataModel> getAccelModels() {
        return accelModels;
    }

    public List<GyroDataModel> getGyroModels() {
        return gyroModels;
    }
}