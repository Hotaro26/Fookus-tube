package com.fookus.tube.util

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.widget.Toast

class AndroidPlatformBridge(private val context: Context) : PlatformBridge {
    override fun showToast(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

    override suspend fun extractMediaInfo(url: String): String {
        return "{}"
    }

    override suspend fun downloadMedia(
        url: String,
        quality: String,
        isAudioOnly: Boolean,
        onProgress: (Float) -> Unit,
        onComplete: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        onError("Downloading not supported in FookusTube")
    }

    override fun openSavedFolder(path: String) {
    }

    override fun saveSetting(key: String, value: String) {
    }

    override fun getSetting(key: String, defaultValue: String): String {
        return defaultValue
    }
}
