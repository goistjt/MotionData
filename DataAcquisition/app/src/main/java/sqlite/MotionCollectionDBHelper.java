package sqlite;

import android.content.ContentValues;
import android.content.Context;
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

    public MotionCollectionDBHelper(Context context) {
        super(context, context.getString(R.string.DBName), null, 1);
        mContext = context;
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(mContext.getString(R.string.CreateAccelDataTable));
        db.execSQL(mContext.getString(R.string.CreateGyroDataTable));
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL(mContext.getString(R.string.DropAccelDataTable));
        db.execSQL(mContext.getString(R.string.DropGyroDataTable));
        onCreate(db);
    }

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
                db.insert(mContext.getString(R.string.AccelerationTableName), null, values);
            }
            db.setTransactionSuccessful();
        }
        finally {
            db.endTransaction();
            Log.d("ACCEL_STACK", String.valueOf(mAccelStack.size()));
            Log.d("ACCEL_COUNT", String.valueOf(DatabaseUtils.queryNumEntries(db, "Accel_Data")));
        }
    }

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
                db.insert(mContext.getString(R.string.GyroscopeTableName), null, values);
            }
            db.setTransactionSuccessful();
        }
        finally {
            db.endTransaction();
            Log.d("GYRO_STACK", String.valueOf(mGyroStack.size()));
            Log.d("GYRO_COUNT", String.valueOf(DatabaseUtils.queryNumEntries(db, "Gyro_Data")));
        }
    }

    public void insertAccelData(AccelDataModel data) {
        mAccelStack.push(data);
    }

    public void insertGyroData(GyroDataModel data) {
        mGyroStack.push(data);
    }

    public long deleteCurrentAccelData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.DeleteAccelData));
        long rowId = statement.executeUpdateDelete();
        Log.d("ACCEL_ROW", String.valueOf(rowId));
        return rowId;
    }

    public long deleteCurrentGyroData() {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(mContext.getString(R.string.DeleteGyroData));
        long rowId = statement.executeUpdateDelete();
        Log.d("GYRO_ROW", String.valueOf(rowId));
        return rowId;
    }
}