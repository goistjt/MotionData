package datamodels;

import java.util.List;

/**
 * Created by steve on 10/10/16.
 */

public class SessionModel {

    private List<AccelDataModel> accelModels;
    private List<GyroDataModel> gyroModels;
    private String device_id;
    private String sess_desc;
    private long begin;
    private long sess_id;

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

    public SessionModel setDeviceId(String deviceId) {
        this.device_id = deviceId;
        return this;
    }

    public SessionModel setSessDesc(String sessDesc) {
        this.sess_desc = sessDesc;
        return this;
    }

    public SessionModel setStartTime(long startTime) {
        this.begin = startTime;
        return this;
    }

    public void setSessId(long sessId) {
        this.sess_id = sessId;
    }

    public long getSessId() {
        return sess_id;
    }
}