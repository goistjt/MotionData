package datamodels;

/**
 * Created by steve on 9/9/16.
 */
public class AccelDataModel {

    private double x_val;
    private double y_val;
    private double z_val;
    private long time_val;

    public AccelDataModel(long time, double x, double y, double z){
        x_val = x;
        y_val = y;
        z_val = z;
        time_val = time;
    }

    public double getX(){
        return x_val;
    }

    public double getY(){
        return y_val;
    }

    public double getZ(){
        return z_val;
    }

    public long getTime(){
        return time_val;
    }
}