package com.factcues.postmaker;

import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.webkit.JavascriptInterface;

import java.io.OutputStream;

public class SaveBridge {
    private final Context ctx;

    SaveBridge(Context ctx) {
        this.ctx = ctx;
    }

    /** Saves a PNG (base64) into Pictures/FactCues. Returns "ok" or "error: ...". */
    @JavascriptInterface
    public String save(String base64, String filename) {
        try {
            byte[] data = Base64.decode(base64, Base64.DEFAULT);
            ContentResolver resolver = ctx.getContentResolver();

            ContentValues values = new ContentValues();
            values.put(MediaStore.Images.Media.DISPLAY_NAME, filename);
            values.put(MediaStore.Images.Media.MIME_TYPE, "image/png");
            values.put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/FactCues");
            values.put(MediaStore.Images.Media.IS_PENDING, 1);

            Uri uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values);
            if (uri == null) return "error: could not create file";

            try (OutputStream os = resolver.openOutputStream(uri)) {
                if (os == null) return "error: could not open file";
                os.write(data);
            }

            values.clear();
            values.put(MediaStore.Images.Media.IS_PENDING, 0);
            resolver.update(uri, values, null, null);
            return "ok";
        } catch (Exception e) {
            return "error: " + e.getMessage();
        }
    }
}
