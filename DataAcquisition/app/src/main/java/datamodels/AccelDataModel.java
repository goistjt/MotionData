package datamodels;

/**
 * Created by steve on 9/9/16.
 */
public class AccelDataModel {

    private double x_val;
    private double y_val;
    private double z_val;
    private long time_val;

    public AccelDataModel(double x, double y, double z, long time){
        x_val = x;
        y_val = y;
        z_val = z;
        time_val = time;
    }

    public double GetXVal(){
        return x_val;
    }

    public double GetYVal(){
        return y_val;
    }

    public double GetZVal(){
        return z_val;
    }

    public double GetTimeOfOccurrence(){
        return time_val;
    }
}