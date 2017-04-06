package edu.rose_hulman.nswccrane.dataacquisition.utils;


import android.util.Base64;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.zip.GZIPOutputStream;

/**
 * Created by Jeremiah Goist on 1/31/2017.
 */

public class StringComressor {

    public static String compressString(String src) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        GZIPOutputStream zout = null;
        try {
            zout = new GZIPOutputStream(out);
            zout.write(src.getBytes());
            zout.close();
        } catch (IOException e) {
            e.printStackTrace();
        } 
        byte[] bytes = out.toByteArray();
        return Base64.encodeToString(bytes, Base64.DEFAULT);
    }
}
