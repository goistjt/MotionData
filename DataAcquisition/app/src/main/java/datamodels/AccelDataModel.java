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

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        AccelDataModel that = (AccelDataModel) o;

        return time_val == that.time_val;

    }

    @Override
    public int hashCode() {
        return (int) (time_val ^ (time_val >>> 32));
    }
}