package datamodels;

/**
 * Created by steve on 9/9/16.
 */
public class AccelDataModel {

    private double x_val;
    private double y_val;
    private double z_val;
    private long time_val;

    public AccelDataModel(long time, double x, double y, double z) {
        x_val = x;
        y_val = y;
        z_val = z;
        time_val = time;
    }

    public double getX() {
        return x_val;
    }

    public void setX(double x) {
        this.x_val = x;
    }

    public double getY() {
        return y_val;
    }

    public void setY(double y) {
        this.y_val = y;
    }

    public double getZ() {
        return z_val;
    }

    public void setZ(double z) {
        this.z_val = z;
    }

    public long getTime() {
        return time_val;
    }
}