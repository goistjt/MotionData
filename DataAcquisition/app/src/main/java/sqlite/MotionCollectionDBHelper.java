package sqlite;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteStatement;
import android.util.Log;

import java.util.concurrent.Semaphore;

import datamodels.AccelDataModel;

/**
 * Created by steve on 9/14/16.
 */
public class MotionCollectionDBHelper extends SQLiteOpenHelper {

    private static final String INSERT_INTO_ACCEL_DATA = "INSERT INTO Accel_Data(timestamp, x, y, z) VALUES (?, ?, ?, ?)";
    private static final String DELETE_ALL_ACCEL_DATA = "DELETE FROM Accel_Data";

    private Semaphore mInsertionSemaphore;

    public MotionCollectionDBHelper(Context context, Semaphore insertionSemaphore) {
        super(context, "MotionCollectionDB", null, 1);
        mInsertionSemaphore = insertionSemaphore;
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE Accel_Data(timestamp UNSIGNED BIGINT PRIMARY KEY, x DOUBLE, y DOUBLE, z DOUBLE)");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS Accel_Data");
        onCreate(db);
    }

    public long InsertModelIntoDB(AccelDataModel data) {
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(INSERT_INTO_ACCEL_DATA);
        statement.bindLong(1, data.getTime());
        statement.bindDouble(2, data.getX());
        statement.bindDouble(3, data.getY());
        statement.bindDouble(4, data.getZ());
        long rowId = 0;
        try {
            mInsertionSemaphore.acquire();
        } catch (InterruptedException e) {
            Log.e("ACQ_INT_INS", e.getMessage());
        }
        try {
            rowId = statement.executeInsert();
            Log.d("ROW", String.valueOf(rowId));
        }
        catch (Exception e) {
            mInsertionSemaphore.release();
        }
        finally {
            mInsertionSemaphore.release();
        }
        return rowId;
    }

    public long DeleteCurrentAccelData(){
        SQLiteStatement statement = this.getWritableDatabase().compileStatement(DELETE_ALL_ACCEL_DATA);
        long rowId = statement.executeInsert();
        Log.d("ROW", String.valueOf(rowId));
        return rowId;
    }
}