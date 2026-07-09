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

    fun startMockDownload(video: SavedVideo, quality: String, format: String, context: Context) {
        viewModelScope.launch(Dispatchers.IO) {
            consoleLogs.add("fookus@tube: ~$ fookus-dl -f $quality $format ${video.url}")
            delay(500)
            consoleLogs.add("[newpipe] Extracting URL: ${video.url}")
            try {
                org.schabi.newpipe.extractor.NewPipe.init(com.fookus.tube.api.OkHttpDownloader())
                val extractor = org.schabi.newpipe.extractor.ServiceList.YouTube.getStreamExtractor(video.url)
                extractor.fetchPage()
                val streamUrl = if (format == "audio") {
                    extractor.audioStreams.firstOrNull()?.content
                } else {
                    extractor.videoStreams.firstOrNull()?.content
                }

                if (streamUrl != null) {
                    consoleLogs.add("[download] Found stream URL!")
                    consoleLogs.add("[download] Delegating to Android DownloadManager...")
                    
                    val actualTitle = extractor.name ?: video.title
                    val actualUploader = extractor.uploaderName ?: video.uploader
                    val actualThumb = extractor.thumbnails?.firstOrNull()?.url ?: video.thumbUrl

                    val request = android.app.DownloadManager.Request(Uri.parse(streamUrl))
                    request.setTitle(actualTitle)
                    request.setDescription("Downloading via FookusTube")
                    request.setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                    val fileName = "${actualTitle.replace(Regex("[^a-zA-Z0-9.-]"), "_")}.mp4"
                    request.setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, fileName)
                    
                    val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
                    downloadManager.enqueue(request)
                    
                    delay(500)
                    consoleLogs.add("Download queued successfully in Android system!")
                    val savedWithUri = video.copy(
                        title = actualTitle,
                        uploader = actualUploader,
                        thumbUrl = actualThumb,
                        localUri = "file:///storage/emulated/0/Download/$fileName"
                    )
                    withContext(Dispatchers.Main) {
                        addToOffline(savedWithUri)
                    }
                } else {
                    consoleLogs.add("[error] Could not extract stream URL.")
                }
            } catch (e: Exception) {
                consoleLogs.add("[error] Failed to download: ${e.message}")
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
