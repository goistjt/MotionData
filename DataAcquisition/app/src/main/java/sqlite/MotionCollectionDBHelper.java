package sqlite;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteStatement;
import android.support.annotation.NonNull;
import android.util.Log;

import com.google.gson.Gson;

import java.util.ArrayList;
import java.util.List;
import java.util.Stack;
import java.util.concurrent.Semaphore;

import datamodels.AccelDataModel;
import datamodels.GyroDataModel;
import datamodels.SessionModel;
import datamodels.TimeframeDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;

/**
 * Created by steve on 9/14/16.
 */
public class MotionCollectionDBHelper extends SQLiteOpenHelper {

    private final int MAX_STACK_SIZE = 100;

    private final Stack<AccelDataModel> mAccelStack = new Stack<>();
    private final Stack<GyroDataModel> mGyroStack = new Stack<>();

    private Context mContext;

    private Semaphore mBlockAccelPushSemaphore;
    private Semaphore mBlockGyroPushSemaphore;
    private Semaphore mBlockAccelCheckSemaphore;
    private Semaphore mBlockGyroCheckSemaphore;

    private long currentStartTime;
    private long currentEndTime;
    private String start;
    private String end;

    public MotionCollectionDBHelper(Context context) {
        super(context, context.getString(R.string.db_name), null, 1);
        mContext = context;
        currentStartTime = 0;
        currentEndTime = 0;
        mBlockGyroPushSemaphore = new Semaphore(1);
        mBlockAccelPushSemaphore = new Semaphore(1);
        mBlockGyroCheckSemaphore = new Semaphore(1);
        mBlockAccelCheckSemaphore = new Semaphore(1);
        // onUpgrade(getWritableDatabase(), 0, 0);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(mContext.getString(R.string.create_accel_data_table));
        db.execSQL(mContext.getString(R.string.create_gyro_data_table));
        db.execSQL(mContext.getString(R.string.create_timeframe_table));
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL(mContext.getString(R.string.drop_accel_data_table));
        db.execSQL(mContext.getString(R.string.drop_gyro_data_table));
        db.execSQL(mContext.getString(R.string.drop_timeframe_table));
        onCreate(db);
    }

    /**
     * Caches a start time for later use in updating the Timeframe table
     *
     * @param startTime time the recording started, in milliseconds since the epoch
     */
    public void setStartTime(long startTime) {
        currentStartTime = startTime;
    }

    /**
     * Creates a row in the Timeframe table with a cached startTime, and the provided endTime
     *
     * @param endTime time that the recording ended, in milliseconds since the epoch
     */
    public void setEndTime(long endTime) {
        currentEndTime = endTime;
        SQLiteDatabase db = this.getWritableDatabase();
        db.beginTransaction();
        try {
            ContentValues values = new ContentValues();
            values.put(mContext.getString(R.string.start_time), currentStartTime);
            values.put(mContext.getString(R.string.end_time), currentEndTime);
            db.insert(mContext.getString(R.string.timeframe_table_name), null, values);
            db.setTransactionSuccessful();
        } catch (Exception ex) {
            Log.e("TIME_INS", ex.getMessage());
        } finally {
            db.endTransaction();
            db.close();
            currentStartTime = 0;
            currentEndTime = 0;
        }
    }

    /**
     * @param startTime times to search from, in milliseconds since the epoch
     * @param endTime   times to search until, in milliseconds since the epoch
     * @return List of all Timeframes for which data has been recorded
     */
    public List<TimeframeDataModel> getAllTimeframesBetween(long startTime, long endTime) {
        Cursor timeframeCursor;
        List<TimeframeDataModel> timeframeList = new ArrayList<>();
        try (SQLiteDatabase db = this.getReadableDatabase()) {
            timeframeCursor = db.query(false, mContext.getString(R.string.timeframe_table_name), null, mContext.getString(R.string.timeframe_select_query), new String[]{String.valueOf(startTime), String.valueOf(endTime)}, null, null, null, null);
            if (timeframeCursor == null) {
                db.close();
                return timeframeList;
            }
            int startTimeIndex = timeframeCursor.getColumnIndex(mContext.getString(R.string.start_time));
            int endTimeIndex = timeframeCursor.getColumnIndex(mContext.getString(R.string.end_time));
            timeframeCursor.moveToFirst();
            while (!timeframeCursor.isAfterLast()) {
                TimeframeDataModel newModel = new TimeframeDataModel(timeframeCursor.getLong(startTimeIndex), timeframeCursor.getLong(endTimeIndex));
                timeframeList.add(newModel);
                timeframeCursor.moveToNext();
            }
            timeframeCursor.close();
        } catch (Exception ex) {
            Log.e("TIMES_BTWN", ex.getMessage());
            timeframeList = new ArrayList<>();
        }
        return timeframeList;
    }

    /**
     * @param startTime times to search from, in milliseconds since the epoch
     * @param endTime   times to search until, in milliseconds since the epoch
     * @return SessionModel containing all the Accel and Gyro data between the startTime and endTime
     */
    public SessionModel getAllDataBetween(long startTime, long endTime) {
        Cursor accelCursor;
        Cursor gyroCursor;
        List<AccelDataModel> accelModels = new ArrayList<>();
        List<GyroDataModel> gyroModels = new ArrayList<>();
        SessionModel sessionModel;
        try (SQLiteDatabase db = this.getReadableDatabase()) {
            accelCursor = db.query(false, mContext.getString(R.string.acceleration_table_name), null, mContext.getString(R.string.accel_select_query), new String[]{String.valueOf(startTime), String.valueOf(endTime)}, null, null, null, null);
            gyroCursor = db.query(false, mContext.getString(R.string.gyroscope_table_name), null, mContext.getString(R.string.gyro_select_query), new String[]{String.valueOf(startTime), String.valueOf(endTime)}, null, null, null, null);
            if (accelCursor != null) {
                int timestampIndex = accelCursor.getColumnIndex(mContext.getString(R.string.timestamp));
                int xIndex = accelCursor.getColumnIndex(mContext.getString(R.string.x));
                int yIndex = accelCursor.getColumnIndex(mContext.getString(R.string.y));
                int zIndex = accelCursor.getColumnIndex(mContext.getString(R.string.z));
                accelCursor.moveToFirst();
                while (!accelCursor.isAfterLast()) {
                    AccelDataModel newModel = new AccelDataModel(accelCursor.getLong(timestampIndex), accelCursor.getDouble(xIndex), accelCursor.getDouble(yIndex), accelCursor.getDouble(zIndex));
                    accelModels.add(newModel);
                    accelCursor.moveToNext();
                }
                accelCursor.close();
            }
            if (gyroCursor != null) {
                int timestampIndex = gyroCursor.getColumnIndex(mContext.getString(R.string.timestamp));
                int pitchIndex = gyroCursor.getColumnIndex(mContext.getString(R.string.pitch));
                int rollIndex = gyroCursor.getColumnIndex(mContext.getString(R.string.roll));
                int yawIndex = gyroCursor.getColumnIndex(mContext.getString(R.string.yaw));
                gyroCursor.moveToFirst();
                while (!gyroCursor.isAfterLast()) {
                    GyroDataModel newModel = new GyroDataModel(gyroCursor.getLong(timestampIndex), gyroCursor.getDouble(pitchIndex), gyroCursor.getDouble(rollIndex), gyroCursor.getDouble(yawIndex));
                    gyroModels.add(newModel);
                    gyroCursor.moveToNext();
                }
                gyroCursor.close();
            }
            sessionModel = new SessionModel(accelModels, gyroModels);
        } catch (Exception ex) {
            Log.e("TIMES_BTWN", ex.getMessage());
            sessionModel = new SessionModel(new ArrayList<AccelDataModel>(), new ArrayList<GyroDataModel>());
        }
        return sessionModel;

    }

    /**
     * @param startTime times to search from, in milliseconds since the epoch
     * @param endTime   times to search until, in milliseconds since the epoch
     * @return All Acceleration and Gyroscope data between the startTime and endTime formatted as a JSON String
     */
    public String getAllDataAsJson(long startTime, long endTime) {
        SessionModel session = getAllDataBetween(startTime, endTime);
        Gson gson = new Gson();
        return gson.toJson(session);
    }

    /**
     * Pushes a Stack filled with Acceleration data into the database
     */
    public void pushAccelData() {
        SQLiteDatabase db = this.getWritableDatabase();
        try {
            mBlockAccelPushSemaphore.acquire();
        } catch (InterruptedException e) {
            e.printStackTrace();
            db.close();
            return;
        }
        db.beginTransaction();
        try {
            ContentValues values = new ContentValues();
            while (!mAccelStack.isEmpty()) {
                AccelDataModel data = mAccelStack.pop();
                values.put(mContext.getString(R.string.timestamp), data.getTime());
                values.put(mContext.getString(R.string.x), data.getX());
                values.put(mContext.getString(R.string.y), data.getY());
                values.put(mContext.getString(R.string.z), data.getZ());
                db.insert(mContext.getString(R.string.acceleration_table_name), null, values);
            }
            db.setTransactionSuccessful();
        } catch (Exception ex) {
            Log.e("PUSH_ACCEL", ex.getMessage());
        } finally {
            db.endTransaction();
            db.close();
            mBlockAccelPushSemaphore.release();
        }
    }

    /**
     * Pushes a Stack filled with Gyroscope data into the database
     */
    public void pushGyroData() {
        SQLiteDatabase db = this.getWritableDatabase();
        try {
            mBlockGyroPushSemaphore.acquire();
        } catch (InterruptedException e) {
            e.printStackTrace();
            db.close();
            return;
        }
        db.beginTransaction();
        try {
            ContentValues values = new ContentValues();
            while (!mGyroStack.isEmpty()) {
                GyroDataModel data = mGyroStack.pop();
                values.put(mContext.getString(R.string.timestamp), data.getTime());
                values.put(mContext.getString(R.string.pitch), data.getPitch());
                values.put(mContext.getString(R.string.roll), data.getRoll());
                values.put(mContext.getString(R.string.yaw), data.getYaw());
                db.insert(mContext.getString(R.string.gyroscope_table_name), null, values);
            }
            db.setTransactionSuccessful();
        } catch (Exception ex) {
            Log.e("PUSH_ACCEL", ex.getMessage());
        } finally {
            db.endTransaction();
            db.close();
            mBlockGyroPushSemaphore.release();
        }
    }

    /**
     * Pushes a single {@link AccelDataModel} onto a Stack which is periodically inserted into the Acceleration table
     *
     * @param data {@link AccelDataModel}
     */
    public void insertAccelData(@NonNull AccelDataModel data) {
        mAccelStack.push(data);
        try {
            mBlockAccelCheckSemaphore.acquire();
        } catch (InterruptedException e) {
            e.printStackTrace();
            return;
        }
        if (mAccelStack.size() == MAX_STACK_SIZE) {
            mBlockAccelCheckSemaphore.release();
            pushAccelData();
            return;
        }
        mBlockAccelCheckSemaphore.release();
    }

    /**
     * Pushes a single {@link GyroDataModel} onto a Stack which is periodically inserted into the Gyroscope table
     *
     * @param data {@link GyroDataModel}
     */
    public void insertGyroData(@NonNull GyroDataModel data) {
        mGyroStack.push(data);
        try {
            mBlockGyroCheckSemaphore.acquire();
        } catch (InterruptedException e) {
            e.printStackTrace();
            return;
        }
        if (mGyroStack.size() == MAX_STACK_SIZE) {
            mBlockGyroCheckSemaphore.release();
            pushGyroData();
            return;
        }
        mBlockGyroCheckSemaphore.release();
    }

    /**
     * Wipes the Acceleration table
     *
     * @return number of rows deleted
     */
    public long deleteCurrentAccelData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.delete_accel_data));
        return (long) statement.executeUpdateDelete();
    }

    /**
     * Wipes the Gyroscope tables
     *
     * @return number of rows deleted
     */
    public long deleteCurrentGyroData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.delete_gyro_data));
        return (long) statement.executeUpdateDelete();
    }

    /**
     * Wipes the Timeframe table
     *
     * @return number of rows deleted
     */
    public long deleteCurrentTimeframeData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.delete_timeframe));
        return (long) statement.executeUpdateDelete();
    }

    /**
     * Deletes all data in the Acceleration, Gyroscope, and Timeframe tables between the input value
     *
     * @param startTime times to delete from, in milliseconds since the epoch
     * @param endTime   times to deletes until, in milliseconds since the epoch
     */
    public void deleteDataBetween(long startTime, long endTime) {
        SQLiteDatabase db = this.getReadableDatabase();
        String ts = mContext.getString(R.string.timestamp);
        start = String.valueOf(startTime);
        end = String.valueOf(endTime);
        db.delete(mContext.getString(R.string.acceleration_table_name),
                String.format("%s >= ? AND %s <= ?", ts, ts),
                new String[]{start, end});
        db.delete("Timeframe",
                "start_time >= ? AND end_time <= ?",
                new String[]{start, end});
        db.delete(mContext.getString(R.string.gyroscope_table_name),
                String.format("%s >= ? AND %s <= ?", ts, ts),
                new String[]{start, end});
    }
}