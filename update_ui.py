import os

vm_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderViewModel.kt"
vm_code = """package com.fookus.tube.ui

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

class DownloaderViewModel(application: Application) : AndroidViewModel(application) {
    private val prefs = application.getSharedPreferences("fookus_prefs", Context.MODE_PRIVATE)

    // App Preferences
    val themeMode = mutableIntStateOf(0)
    val selectedTheme = mutableStateOf(AppTheme.Default)
    val selectedFolderUri = mutableStateOf<Uri?>(null)
    val selectedFolderName = mutableStateOf<String?>(null)
    val terminalTheme = mutableStateOf(0)

    val history = mutableStateOf<List<SavedVideo>>(emptyList())
    val offline = mutableStateOf<List<SavedVideo>>(emptyList())
    val lastPlayedUrl = mutableStateOf<String?>(null)

    init {
        loadHistoryAndOffline()
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

    fun addToOffline(video: SavedVideo) {
        val current = offline.value.toMutableList()
        current.removeAll { it.url == video.url }
        current.add(0, video)
        offline.value = current
        prefs.edit().putString("offline", Json.encodeToString(current)).apply()
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
"""
with open(vm_path, "w") as f:
    f.write(vm_code)

screen_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"
screen_code = """package com.fookus.tube.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.fookus.tube.model.SavedVideo
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.schabi.newpipe.extractor.ServiceList
import org.schabi.newpipe.extractor.stream.StreamInfoItem
import android.widget.Toast
import androidx.compose.ui.platform.LocalContext

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NewPipeTab(
    viewModel: DownloaderViewModel,
    contentPadding: PaddingValues,
    onUrlSelected: (String) -> Unit
) {
    var query by viewModel.newPipeQuery
    var results by viewModel.newPipeResults
    var isLoading by remember { mutableStateOf(false) }
    var selectedFilter by remember { mutableStateOf("Search") } // "Search", "History", "Offline"
    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current

    val history by viewModel.history
    val offline by viewModel.offline

    val performSearch = {
        if (query.isNotBlank()) {
            selectedFilter = "Search"
            isLoading = true
            coroutineScope.launch(Dispatchers.IO) {
                try {
                    val searchExtractor = ServiceList.YouTube.getSearchExtractor(query)
                    searchExtractor.fetchPage()
                    val items = searchExtractor.initialPage.items.filterIsInstance<StreamInfoItem>()
                    withContext(Dispatchers.Main) {
                        results = items
                        isLoading = false
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                    withContext(Dispatchers.Main) {
                        isLoading = false
                    }
                }
            }
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.fillMaxSize().padding(contentPadding).padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.Top,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth().padding(top = 16.dp, bottom = 8.dp),
                placeholder = { Text("Search YouTube...") },
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                keyboardActions = KeyboardActions(onSearch = { performSearch() }),
                trailingIcon = {
                    if (query.isNotEmpty()) {
                        IconButton(onClick = { query = ""; results = emptyList() }) {
                            Icon(Icons.Default.Close, contentDescription = "Clear")
                        }
                    } else {
                        IconButton(onClick = { performSearch() }) {
                            Icon(Icons.Default.Search, contentDescription = "Search")
                        }
                    }
                },
                shape = MaterialTheme.shapes.large
            )
            
            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = selectedFilter == "History",
                    onClick = { selectedFilter = if (selectedFilter == "History") "Search" else "History" },
                    label = { Text("History") }
                )
                FilterChip(
                    selected = selectedFilter == "Offline",
                    onClick = { selectedFilter = if (selectedFilter == "Offline") "Search" else "Offline" },
                    label = { Text("Offline") }
                )
            }
            
            if (isLoading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else {
                val listToShow = when (selectedFilter) {
                    "History" -> history
                    "Offline" -> offline
                    else -> results.map { 
                        SavedVideo(it.url, it.name, it.uploaderName, it.thumbnails?.firstOrNull()?.url ?: "")
                    }
                }
                
                if (listToShow.isEmpty()) {
                    Spacer(modifier = Modifier.fillMaxHeight(0.2f))
                    Icon(
                        painter = androidx.compose.ui.res.painterResource(android.R.drawable.ic_media_play),
                        contentDescription = "YouTube",
                        modifier = Modifier.size(72.dp).padding(bottom = 16.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Text(
                        if (selectedFilter == "Search") "YouTube Search" else selectedFilter,
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                    )
                } else {
                    LazyColumn(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(listToShow) { item ->
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                onClick = { 
                                    viewModel.addToHistory(item)
                                    onUrlSelected(item.url) 
                                },
                                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
                            ) {
                                Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Box(modifier = Modifier.size(100.dp, 60.dp)) {
                                        AsyncImage(
                                            model = item.thumbUrl,
                                            contentDescription = null,
                                            modifier = Modifier.fillMaxSize(),
                                            contentScale = androidx.compose.ui.layout.ContentScale.Crop
                                        )
                                    }
                                    Spacer(Modifier.width(12.dp))
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(item.title, style = MaterialTheme.typography.titleSmall, maxLines = 2, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold)
                                        Spacer(Modifier.height(4.dp))
                                        Text(item.uploader, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                    }
                                    if (selectedFilter == "Search") {
                                        IconButton(onClick = { 
                                            // Mock Download - add to offline
                                            viewModel.addToOffline(item)
                                            Toast.makeText(context, "Added to Offline!", Toast.LENGTH_SHORT).show()
                                        }) {
                                            Icon(Icons.Default.Download, "Download", tint = MaterialTheme.colorScheme.primary)
                                        }
                                    }
                                }
                            }
                        }
                        item { Spacer(Modifier.height(80.dp)) }
                    }
                }
            }
        }
        
        // Floating Continue Button
        val lastPlayed = viewModel.lastPlayedUrl.value
        if (lastPlayed != null && selectedFilter != "History") {
            FloatingActionButton(
                onClick = { onUrlSelected(lastPlayed) },
                modifier = Modifier.align(Alignment.BottomEnd).padding(end = 16.dp, bottom = 16.dp + contentPadding.calculateBottomPadding()),
                containerColor = MaterialTheme.colorScheme.primary
            ) {
                Icon(Icons.Default.PlayArrow, contentDescription = "Continue playing")
            }
        }
    }
}
"""
with open(screen_path, "w") as f:
    f.write(screen_code)
print("Updated view model and screen.")
