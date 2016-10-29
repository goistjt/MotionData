package sqlite;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteStatement;
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

    public void setStartTime(long startTime) {
        currentStartTime = startTime;
    }

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

    public List<TimeframeDataModel> getAllTimeframesBetween(long startTime, long endTime) {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor timeframeCursor;
        List<TimeframeDataModel> timeframeList = new ArrayList<>();
        try {
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
        finally {
            db.close();
        }
        return timeframeList;
    }

    public SessionModel getAllDataBetween(long startTime, long endTime) {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor accelCursor;
        Cursor gyroCursor;
        List<AccelDataModel> accelModels = new ArrayList<>();
        List<GyroDataModel> gyroModels = new ArrayList<>();
        SessionModel sessionModel;
        try {
            accelCursor = db.query(false, mContext.getString(R.string.acceleration_table_name), null, mContext.getString(R.string.accel_select_query), new String[]{String.valueOf(startTime), String.valueOf(endTime)}, null, null, null, null);
            gyroCursor = db.query(false, mContext.getString(R.string.gyroscope_table_name), null, mContext.getString(R.string.gyro_select_query), new String[]{String.valueOf(startTime), String.valueOf(endTime)}, null, null, null, null);
            if (accelCursor != null) {
                int timestampIndex = accelCursor.getColumnIndex(mContext.getString(R.string.timestamp));
                int xIndex = accelCursor.getColumnIndex(mContext.getString(R.string.x));
                int yIndex = accelCursor.getColumnIndex(mContext.getString(R.string.y));
                int zIndex = accelCursor.getColumnIndex(mContext.getString(R.string.z));
                accelCursor.moveToFirst();
                while (!accelCursor.isAfterLast()) {
                    AccelDataModel newModel = new AccelDataModel(accelCursor.getLong(timestampIndex), accelCursor.getLong(xIndex), accelCursor.getLong(yIndex), accelCursor.getLong(zIndex));
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
                    GyroDataModel newModel = new GyroDataModel(gyroCursor.getLong(timestampIndex), gyroCursor.getLong(pitchIndex), gyroCursor.getLong(rollIndex), gyroCursor.getLong(yawIndex));
                    gyroModels.add(newModel);
                    gyroCursor.moveToNext();
                }
                gyroCursor.close();
            }
            sessionModel = new SessionModel(accelModels, gyroModels);
        } catch (Exception ex) {
            Log.e("TIMES_BTWN", ex.getMessage());
            sessionModel = new SessionModel(new ArrayList<AccelDataModel>(), new ArrayList<GyroDataModel>());
        } finally {
            db.close();
        }
        return sessionModel;

    }

    public String getAllDataAsJson(long startTime, long endTime) {
        SessionModel session = getAllDataBetween(startTime, endTime);
        Gson gson = new Gson();
        return gson.toJson(session);
    }

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
        } catch(Exception ex) {
            Log.e("PUSH_ACCEL", ex.getMessage());
        } finally {
            db.endTransaction();
            db.close();
            mBlockAccelPushSemaphore.release();
        }
    }

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
        } catch(Exception ex) {
            Log.e("PUSH_ACCEL", ex.getMessage());
        } finally {
            db.endTransaction();
            db.close();
            mBlockGyroPushSemaphore.release();
        }
    }

    public void insertAccelData(AccelDataModel data) {
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

    public void insertGyroData(GyroDataModel data) {
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


    public long deleteCurrentAccelData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.delete_accel_data));
        long rowId = statement.executeUpdateDelete();
        return rowId;
    }

    public long deleteCurrentGyroData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.delete_gyro_data));
        long rowId = statement.executeUpdateDelete();
        return rowId;
    }

    public long deleteCurrentTimeframeData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.delete_timeframe));
        long rowId = statement.executeUpdateDelete();
        return rowId;
    }
}