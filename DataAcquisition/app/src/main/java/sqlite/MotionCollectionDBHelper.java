package sqlite;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.DatabaseUtils;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteStatement;
import android.util.Log;
import java.util.Stack;
import datamodels.AccelDataModel;
import datamodels.GyroDataModel;
import edu.rose_hulman.nswccrane.dataacquisition.R;
import sqlite.interfaces.ICollectionDBHelper;

/**
 * Created by steve on 9/14/16.
 */
public class MotionCollectionDBHelper extends SQLiteOpenHelper implements ICollectionDBHelper {

    private final Stack<AccelDataModel> mAccelStack = new Stack<>();
    private final Stack<GyroDataModel> mGyroStack = new Stack<>();
    private Context mContext;
    private long currentStartTime;
    private long currentEndTime;

    public MotionCollectionDBHelper(Context context) {
        super(context, context.getString(R.string.db_name), null, 1);
        mContext = context;
        currentStartTime = 0;
        currentEndTime = 0;
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

    @Override
    public void setStartTime(long startTime) {
        currentStartTime = startTime;
    }

    @Override
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
        }
        finally {
            db.endTransaction();
            Log.d("START", String.valueOf(currentStartTime));
            Log.d("END", String.valueOf(currentEndTime));
            currentStartTime = 0;
            currentEndTime = 0;
        }
    }

    @Override
    public void getAllTimeframesBetween(long startTime, long endTime) {
        SQLiteDatabase db = this.getWritableDatabase();
        db.beginTransaction();
        try {
            Cursor timeframeCursor = db.rawQuery(mContext.getString(R.string.timeframe_select_query), new String[] {"in_start_time", "in_end_time"});
            Log.d("TIME", String.valueOf(timeframeCursor.getCount()));
        }
        finally {
            db.endTransaction();
        }
    }

    @Override
    public void pushAccelData() {
        SQLiteDatabase db = this.getWritableDatabase();
        db.beginTransaction();
        try{
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
        }
        finally {
            db.endTransaction();
            Log.d("ACCEL_STACK", String.valueOf(mAccelStack.size()));
            Log.d("ACCEL_COUNT", String.valueOf(DatabaseUtils.queryNumEntries(db, "Accel_Data")));
        }
    }

    @Override
    public void pushGyroData() {
        SQLiteDatabase db = this.getWritableDatabase();
        db.beginTransaction();
        try{
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
        }
        finally {
            db.endTransaction();
            Log.d("GYRO_STACK", String.valueOf(mGyroStack.size()));
            Log.d("GYRO_COUNT", String.valueOf(DatabaseUtils.queryNumEntries(db, "Gyro_Data")));
        }
    }

    @Override
    public void insertAccelData(AccelDataModel data) {
        mAccelStack.push(data);
    }

    @Override
    public void insertGyroData(GyroDataModel data) {
        mGyroStack.push(data);
    }

    @Override
    public long deleteCurrentAccelData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.delete_accel_data));
        long rowId = statement.executeUpdateDelete();
        Log.d("ACCEL_ROW", String.valueOf(rowId));
        return rowId;
    }

    @Override
    public long deleteCurrentGyroData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.delete_gyro_data));
        long rowId = statement.executeUpdateDelete();
        Log.d("GYRO_ROW", String.valueOf(rowId));
        return rowId;
    }

    @Override
    public long deleteCurrentTimeframeData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.delete_timeframe));
        long rowId = statement.executeUpdateDelete();
        Log.d("TIME_ROW", String.valueOf(rowId));
        return rowId;
    }
}