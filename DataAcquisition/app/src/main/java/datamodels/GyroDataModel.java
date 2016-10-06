package datamodels;

/**
 * Created by steve on 9/25/16.
 */

public class GyroDataModel {
    private double pitch_val;
    private double roll_val;
    private double yaw_val;
    private long time_val;

    public GyroDataModel(long time, double pitch, double roll, double yaw) {
        pitch_val = pitch;
        roll_val = roll;
        yaw_val = yaw;
        time_val = time;
    }

    public double getPitch(){
        return pitch_val;
    }

    public double getRoll(){
        return roll_val;
    }

    public double getYaw(){
        return yaw_val;
    }

    public long getTime(){
        return time_val;
    }
}
