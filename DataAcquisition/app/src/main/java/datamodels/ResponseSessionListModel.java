package datamodels;

import java.io.Serializable;
import java.util.List;

/**
 * Created by goistjt on 11/4/2016.
 */
public class ResponseSessionListModel implements Serializable {
    private List<ResponseSessionModel> sessions;

    public List<ResponseSessionModel> getSessions() {
        return sessions;
    }

    public void setSessions(List<ResponseSessionModel> sessions) {
        this.sessions = sessions;
    }
}
