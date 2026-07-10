package com.fookus.tube.ui

import android.app.Application
import android.content.Context
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import com.fookus.tube.ui.theme.AppTheme
import org.schabi.newpipe.extractor.stream.StreamInfoItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import android.net.Uri
import com.fookus.tube.model.SavedVideo
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.decodeFromString
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

enum class TerminalTheme(val displayName: String, val background: Long, val header: Long, val text: Long) {
    HACKER("Hacker Green", 0xFF0D1117, 0xFF161B22, 0xFF00FF00),
    DRACULA("Dracula", 0xFF282A36, 0xFF44475A, 0xFFF8F8F2),
    MONOKAI("Monokai", 0xFF272822, 0xFF3E3D32, 0xFFF8F8F2),
    SOLARIZED("Solarized Dark", 0xFF002B36, 0xFF073642, 0xFF839496),
    UBUNTU("Ubuntu", 0xFF300A24, 0xFF5E2750, 0xFFFFFFFF)
}

class DownloaderViewModel(application: Application) : AndroidViewModel(application) {
    private val prefs = application.getSharedPreferences("fookus_prefs", Context.MODE_PRIVATE)

    // App Preferences
    val themeMode = mutableIntStateOf(0)
    val selectedTheme = mutableStateOf(AppTheme.Dynamic)
    val selectedFolderUri = mutableStateOf<Uri?>(null)
    val selectedFolderName = mutableStateOf<String?>(null)
    
    val terminalTheme = mutableStateOf(TerminalTheme.MONOKAI)
    val consoleLogs = androidx.compose.runtime.mutableStateListOf<String>()

    val searchSource = mutableStateOf("YouTube")
    val activeFilter = mutableStateOf("Search")
    val triggerDownloadUrl = mutableStateOf<String?>(null)
    val offlineUrl = mutableStateOf("")
    val history = mutableStateOf<List<SavedVideo>>(emptyList())
    val offline = mutableStateOf<List<SavedVideo>>(emptyList())
    val bookmarks = mutableStateOf<Map<String, List<SavedVideo>>>(mapOf("Watch Later" to emptyList()))
    val lastPlayedUrl = mutableStateOf<String?>(null)

    init {
        loadHistoryAndOffline()
    }

    fun clearConsole() {
        consoleLogs.clear()
    }

    fun updateTerminalTheme(theme: TerminalTheme) {
        terminalTheme.value = theme
    }

    private fun loadHistoryAndOffline() {
        try {
            val histStr = prefs.getString("history", "[]") ?: "[]"
            history.value = Json.decodeFromString(histStr)
            val offStr = prefs.getString("offline", "[]") ?: "[]"
            offline.value = Json.decodeFromString(offStr)
            lastPlayedUrl.value = prefs.getString("last_played", null)
            val bmStr = prefs.getString("bookmarks_list", null)
            if (bmStr != null) {
                bookmarks.value = Json.decodeFromString(bmStr)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun addBookmarkPlaylist(name: String) {
        if (!bookmarks.value.containsKey(name)) {
            val newMap = bookmarks.value.toMutableMap()
            newMap[name] = emptyList()
            bookmarks.value = newMap
            saveBookmarks()
        }
    }

    fun addVideoToBookmark(playlist: String, video: SavedVideo) {
        val newMap = bookmarks.value.toMutableMap()
        val currentList = newMap[playlist]?.toMutableList() ?: mutableListOf()
        if (currentList.none { it.url == video.url }) {
            currentList.add(0, video)
            newMap[playlist] = currentList
            bookmarks.value = newMap
            saveBookmarks()
        }
    }

    fun removeVideoFromBookmark(playlist: String, url: String) {
        val newMap = bookmarks.value.toMutableMap()
        val currentList = newMap[playlist]?.toMutableList() ?: return
        if (currentList.removeAll { it.url == url }) {
            newMap[playlist] = currentList
            bookmarks.value = newMap
            saveBookmarks()
        }
    }

    private fun saveBookmarks() {
        prefs.edit().putString("bookmarks_list", Json.encodeToString(bookmarks.value)).apply()
    }

    fun addToHistory(video: SavedVideo) {
        val current = history.value.toMutableList()
        current.removeAll { it.url == video.url }
        current.add(0, video)
        if (current.size > 50) current.removeLast()
        history.value = current
        lastPlayedUrl.value = video.url
        prefs.edit()
            .putString("history", Json.encodeToString(current))
            .putString("last_played", video.url)
            .apply()
    }

    private fun downloadFile(url: String, outputFile: java.io.File, onProgress: (Int) -> Unit) {
        val client = okhttp3.OkHttpClient.Builder()
            .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .build()
        val request = okhttp3.Request.Builder().url(url).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw java.io.IOException("Failed to download file: $response")
            val body = response.body ?: throw java.io.IOException("Empty response body")
            val totalBytes = body.contentLength()
            body.byteStream().use { inputStream ->
                java.io.FileOutputStream(outputFile).use { outputStream ->
                    val buffer = ByteArray(16 * 1024)
                    var bytesRead: Int
                    var downloadedBytes: Long = 0
                    var lastProgressPercent = -1
                    while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                        outputStream.write(buffer, 0, bytesRead)
                        downloadedBytes += bytesRead
                        if (totalBytes > 0) {
                            val progress = ((downloadedBytes * 100) / totalBytes).toInt()
                            if (progress != lastProgressPercent) {
                                onProgress(progress)
                                lastProgressPercent = progress
                            }
                        }
                    }
                }
            }
        }
    }

    private fun muxVideoAudio(videoFile: java.io.File, audioFile: java.io.File, outputFile: java.io.File) {
        val videoExtractor = android.media.MediaExtractor()
        videoExtractor.setDataSource(videoFile.absolutePath)
        
        val audioExtractor = android.media.MediaExtractor()
        audioExtractor.setDataSource(audioFile.absolutePath)
        
        val muxer = android.media.MediaMuxer(outputFile.absolutePath, android.media.MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4)
        
        var videoTrackIndex = -1
        for (i in 0 until videoExtractor.trackCount) {
            val format = videoExtractor.getTrackFormat(i)
            val mime = format.getString(android.media.MediaFormat.KEY_MIME) ?: ""
            if (mime.startsWith("video/")) {
                videoExtractor.selectTrack(i)
                videoTrackIndex = muxer.addTrack(format)
                break
            }
        }
        
        var audioTrackIndex = -1
        for (i in 0 until audioExtractor.trackCount) {
            val format = audioExtractor.getTrackFormat(i)
            val mime = format.getString(android.media.MediaFormat.KEY_MIME) ?: ""
            if (mime.startsWith("audio/")) {
                audioExtractor.selectTrack(i)
                audioTrackIndex = muxer.addTrack(format)
                break
            }
        }
        
        if (videoTrackIndex == -1) {
            videoExtractor.release()
            audioExtractor.release()
            throw java.io.IOException("Video track not found in source video stream")
        }
        if (audioTrackIndex == -1) {
            videoExtractor.release()
            audioExtractor.release()
            throw java.io.IOException("Audio track not found in source audio stream")
        }

        muxer.start()
        
        val videoBuffer = java.nio.ByteBuffer.allocate(1024 * 1024)
        val videoBufferInfo = android.media.MediaCodec.BufferInfo()
        while (true) {
            videoBufferInfo.offset = 0
            videoBufferInfo.size = videoExtractor.readSampleData(videoBuffer, 0)
            if (videoBufferInfo.size < 0) {
                break
            }
            videoBufferInfo.presentationTimeUs = videoExtractor.sampleTime
            videoBufferInfo.flags = videoExtractor.sampleFlags
            muxer.writeSampleData(videoTrackIndex, videoBuffer, videoBufferInfo)
            videoExtractor.advance()
        }
        
        val audioBuffer = java.nio.ByteBuffer.allocate(1024 * 1024)
        val audioBufferInfo = android.media.MediaCodec.BufferInfo()
        while (true) {
            audioBufferInfo.offset = 0
            audioBufferInfo.size = audioExtractor.readSampleData(audioBuffer, 0)
            if (audioBufferInfo.size < 0) {
                break
            }
            audioBufferInfo.presentationTimeUs = audioExtractor.sampleTime
            audioBufferInfo.flags = audioExtractor.sampleFlags
            muxer.writeSampleData(audioTrackIndex, audioBuffer, audioBufferInfo)
            audioExtractor.advance()
        }
        
        muxer.stop()
        muxer.release()
        videoExtractor.release()
        audioExtractor.release()
    }

    private fun showDownloadNotification(context: Context, id: Int, title: String, text: String, progress: Int, isIndeterminate: Boolean = false) {
        val channelId = "fookus_downloads"
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as android.app.NotificationManager
        
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            val channel = android.app.NotificationChannel(
                channelId,
                "Fookus Tube Downloads",
                android.app.NotificationManager.IMPORTANCE_LOW
            )
            notificationManager.createNotificationChannel(channel)
        }
        
        val builder = androidx.core.app.NotificationCompat.Builder(context, channelId)
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setPriority(androidx.core.app.NotificationCompat.PRIORITY_LOW)
            .setOnlyAlertOnce(true)
            .setOngoing(progress < 100)
            
        if (progress in 0..99) {
            builder.setProgress(100, progress, isIndeterminate)
        } else if (progress >= 100) {
            builder.setProgress(0, 0, false)
            builder.setSmallIcon(android.R.drawable.stat_sys_download_done)
            builder.setOngoing(false)
        }
        
        notificationManager.notify(id, builder.build())
    }

    fun startMockDownload(video: SavedVideo, quality: String, format: String, context: Context) {
        viewModelScope.launch(Dispatchers.IO) {
            val notificationId = video.url.hashCode()
            val qualityClean = quality.replace("p", "")
            consoleLogs.add("fookus@tube: ~$ fookus-dl -f ${qualityClean}p $format ${video.url}")
            delay(500)
            consoleLogs.add("[newpipe] Extracting URL: ${video.url}")
            try {
                org.schabi.newpipe.extractor.NewPipe.init(com.fookus.tube.api.OkHttpDownloader())
                val extractor = org.schabi.newpipe.extractor.ServiceList.YouTube.getStreamExtractor(video.url)
                extractor.fetchPage()
                
                val actualTitle = extractor.name ?: video.title
                val actualUploader = extractor.uploaderName ?: video.uploader
                val actualThumb = extractor.thumbnails?.firstOrNull()?.url ?: video.thumbUrl
                val safeFileName = actualTitle.replace(Regex("[^a-zA-Z0-9.-]"), "_")

                showDownloadNotification(context, notificationId, "Initializing Download", actualTitle, 0, true)

                if (format == "audio") {
                    val audioStream = extractor.audioStreams.firstOrNull()
                    if (audioStream == null) {
                        consoleLogs.add("[error] No audio stream found.")
                        showDownloadNotification(context, notificationId, "Download Failed", "No audio stream found", 100)
                        return@launch
                    }
                    consoleLogs.add("[download] Downloading audio stream...")
                    val destFile = java.io.File(
                        android.os.Environment.getExternalStoragePublicDirectory(android.os.Environment.DIRECTORY_DOWNLOADS),
                        "$safeFileName.m4a"
                    )
                    downloadFile(audioStream.content, destFile) { progress ->
                        if (progress % 10 == 0 || progress == 100) {
                            consoleLogs.add("[download] Audio progress: $progress%")
                            showDownloadNotification(context, notificationId, "Downloading Audio", "$actualTitle - $progress%", progress)
                        }
                    }
                    android.media.MediaScannerConnection.scanFile(context, arrayOf(destFile.absolutePath), null, null)
                    consoleLogs.add("[download] Audio downloaded successfully!")
                    showDownloadNotification(context, notificationId, "Download Completed", actualTitle, 100)
                    val savedWithUri = video.copy(
                        title = actualTitle,
                        uploader = actualUploader,
                        thumbUrl = actualThumb,
                        localUri = "file://${destFile.absolutePath}"
                    )
                    withContext(Dispatchers.Main) {
                        addToOffline(savedWithUri)
                    }
                } else {
                    val progressiveStream = extractor.videoStreams.find { it.resolution.contains(qualityClean) }
                    if (progressiveStream != null) {
                        consoleLogs.add("[download] Found progressive ${qualityClean}p stream. Downloading directly...")
                        val destFile = java.io.File(
                            android.os.Environment.getExternalStoragePublicDirectory(android.os.Environment.DIRECTORY_DOWNLOADS),
                            "$safeFileName.mp4"
                        )
                        downloadFile(progressiveStream.content, destFile) { progress ->
                            if (progress % 10 == 0 || progress == 100) {
                                consoleLogs.add("[download] Progress: $progress%")
                                showDownloadNotification(context, notificationId, "Downloading Video", "$actualTitle - $progress%", progress)
                            }
                        }
                        android.media.MediaScannerConnection.scanFile(context, arrayOf(destFile.absolutePath), null, null)
                        consoleLogs.add("[download] Download completed!")
                        showDownloadNotification(context, notificationId, "Download Completed", actualTitle, 100)
                        val savedWithUri = video.copy(
                            title = actualTitle,
                            uploader = actualUploader,
                            thumbUrl = actualThumb,
                            localUri = "file://${destFile.absolutePath}"
                        )
                        withContext(Dispatchers.Main) {
                            addToOffline(savedWithUri)
                        }
                    } else {
                        val videoOnlyStream = extractor.videoOnlyStreams.find { it.resolution.contains(qualityClean) }
                            ?: extractor.videoOnlyStreams.maxByOrNull { it.resolution.replace(Regex("[^0-9]"), "").toIntOrNull() ?: 0 }
                        
                        if (videoOnlyStream == null) {
                            consoleLogs.add("[error] No video streams found.")
                            showDownloadNotification(context, notificationId, "Download Failed", "No video stream found", 100)
                            return@launch
                        }
                        
                        val audioStream = extractor.audioStreams.firstOrNull()
                        if (audioStream == null) {
                            consoleLogs.add("[error] No audio streams found.")
                            showDownloadNotification(context, notificationId, "Download Failed", "No audio stream found", 100)
                            return@launch
                        }
                        
                        consoleLogs.add("[download] Selected DASH video stream: ${videoOnlyStream.resolution}")
                        
                        val cacheDir = context.cacheDir
                        val tempVideoFile = java.io.File(cacheDir, "temp_video_${System.currentTimeMillis()}.mp4")
                        val tempAudioFile = java.io.File(cacheDir, "temp_audio_${System.currentTimeMillis()}.m4a")
                        val destFile = java.io.File(
                            android.os.Environment.getExternalStoragePublicDirectory(android.os.Environment.DIRECTORY_DOWNLOADS),
                            "$safeFileName.mp4"
                        )
                        
                        consoleLogs.add("[download] Downloading video track...")
                        downloadFile(videoOnlyStream.content, tempVideoFile) { progress ->
                            if (progress % 10 == 0 || progress == 100) {
                                consoleLogs.add("[download] Video track: $progress%")
                                showDownloadNotification(context, notificationId, "Downloading Video", "$actualTitle - ${progress / 2}%", progress / 2)
                            }
                        }
                        
                        consoleLogs.add("[download] Downloading audio track...")
                        downloadFile(audioStream.content, tempAudioFile) { progress ->
                            if (progress % 10 == 0 || progress == 100) {
                                consoleLogs.add("[download] Audio track: $progress%")
                                showDownloadNotification(context, notificationId, "Downloading Audio", "$actualTitle - ${50 + (progress / 2)}%", 50 + (progress / 2))
                            }
                        }
                        
                        consoleLogs.add("[muxer] Muxing video and audio tracks...")
                        showDownloadNotification(context, notificationId, "Muxing Streams", actualTitle, 99, true)
                        try {
                            muxVideoAudio(tempVideoFile, tempAudioFile, destFile)
                            android.media.MediaScannerConnection.scanFile(context, arrayOf(destFile.absolutePath), null, null)
                            consoleLogs.add("[muxer] Muxing completed! Saved to: Downloads/$safeFileName.mp4")
                            showDownloadNotification(context, notificationId, "Download Completed", actualTitle, 100)
                            
                            val savedWithUri = video.copy(
                                title = actualTitle,
                                uploader = actualUploader,
                                thumbUrl = actualThumb,
                                localUri = "file://${destFile.absolutePath}"
                            )
                            withContext(Dispatchers.Main) {
                                addToOffline(savedWithUri)
                            }
                        } finally {
                            tempVideoFile.delete()
                            tempAudioFile.delete()
                        }
                    }
                }
            } catch (e: Exception) {
                consoleLogs.add("[error] Failed to download: ${e.message}")
                showDownloadNotification(context, notificationId, "Download Failed", e.message ?: "Unknown error", 100)
                e.printStackTrace()
            }
        }
    }

    fun addToOffline(video: SavedVideo) {
        val current = offline.value.toMutableList()
        current.removeAll { it.url == video.url }
        current.add(0, video)
        offline.value = current
        prefs.edit().putString("offline", Json.encodeToString(current)).apply()
    }

    fun removeFromHistory(video: SavedVideo) {
        val current = history.value.toMutableList()
        if (current.removeAll { it.url == video.url }) {
            history.value = current
            prefs.edit().putString("history", Json.encodeToString(current)).apply()
        }
    }

    fun removeFromOffline(video: SavedVideo) {
        val current = offline.value.toMutableList()
        if (current.removeAll { it.url == video.url }) {
            offline.value = current
            prefs.edit().putString("offline", Json.encodeToString(current)).apply()
            
            // Delete actual file if exists
            video.localUri?.let { uriString ->
                if (uriString.startsWith("file://")) {
                    val path = uriString.removePrefix("file://")
                    val file = java.io.File(path)
                    if (file.exists()) {
                        file.delete()
                    }
                }
            }
        }
    }

    fun setThemeMode(mode: Int) {
        themeMode.intValue = mode
    }

    fun setAppTheme(theme: AppTheme) {
        selectedTheme.value = theme
    }

    private val _externalUrl = MutableStateFlow<String?>(null)
    val externalUrl: StateFlow<String?> = _externalUrl
    
    fun handleSharedUrl(url: String) {
        _externalUrl.value = url
    }

    fun consumeSharedUrl() {
        _externalUrl.value = null
    }

    val newPipeQuery = mutableStateOf("")
    val newPipeResults = mutableStateOf<List<StreamInfoItem>>(emptyList())
}
