package datamodels;

/**
 * Created by steve on 10/2/16.
 */

public class TimeframeDataModel {

    private long startTime;
    private long endTime;

    public TimeframeDataModel(long start, long end) {
        startTime = start;
        endTime = end;
    }

    public long getStartTime() {
        return startTime;
    }

    public long getEndTime() {
        return endTime;
    }
}
