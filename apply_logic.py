import os
import re

newpipe_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"
with open(newpipe_path, "r") as f:
    np_content = f.read()

# I need to rebuild NewPipeTab to support separate pages for History and Offline.
# Let's write a replacement for the whole NewPipeTab logic to handle this cleaner.
new_newpipe_tab = """package com.fookus.tube.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.BorderStroke
import coil.compose.AsyncImage
import com.fookus.tube.model.SavedVideo
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.schabi.newpipe.extractor.ServiceList
import org.schabi.newpipe.extractor.stream.StreamInfoItem
import android.widget.Toast

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
    var showDownloadDialog by remember { mutableStateOf<SavedVideo?>(null) }
    var selectedQuality by remember { mutableStateOf("720p") }
    var isAudioOnly by remember { mutableStateOf(false) }
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

    if (selectedFilter != "Search") {
        // Separate Page for History or Offline
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text(selectedFilter) },
                    navigationIcon = {
                        IconButton(onClick = { selectedFilter = "Search" }) {
                            Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                        }
                    }
                )
            },
            modifier = Modifier.padding(bottom = contentPadding.calculateBottomPadding())
        ) { innerPadding ->
            val listToShow = if (selectedFilter == "History") history else offline
            Column(modifier = Modifier.padding(innerPadding).padding(horizontal = 16.dp).fillMaxSize()) {
                if (selectedFilter == "Offline") {
                    val currentTerminalTheme = viewModel.terminalTheme.value
                    val consoleLogs = viewModel.consoleLogs
                    Card(
                        modifier = Modifier.fillMaxWidth().height(180.dp).padding(bottom = 16.dp),
                        colors = CardDefaults.cardColors(containerColor = Color(currentTerminalTheme.background)),
                        border = BorderStroke(1.dp, Color(currentTerminalTheme.header)),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Column(modifier = Modifier.fillMaxSize()) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(Color(currentTerminalTheme.header))
                                    .padding(horizontal = 16.dp, vertical = 8.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                    Box(Modifier.size(8.dp).background(Color(0xFFFF5F56), CircleShape))
                                    Box(Modifier.size(8.dp).background(Color(0xFFFFBD2E), CircleShape))
                                    Box(Modifier.size(8.dp).background(Color(0xFF27C93F), CircleShape))
                                }
                                Text(
                                    text = "fookus@tube: ~",
                                    color = Color(currentTerminalTheme.text).copy(alpha = 0.6f),
                                    style = MaterialTheme.typography.labelSmall,
                                    fontFamily = FontFamily.Monospace
                                )
                                IconButton(
                                    onClick = { viewModel.clearConsole() },
                                    modifier = Modifier.size(16.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Delete,
                                        contentDescription = "Clear Console",
                                        tint = Color(currentTerminalTheme.text).copy(alpha = 0.6f),
                                        modifier = Modifier.size(12.dp)
                                    )
                                }
                            }
                            HorizontalDivider(color = Color(currentTerminalTheme.header), thickness = 1.dp)
                            val lazyListState = rememberLazyListState()
                            LaunchedEffect(consoleLogs.size) {
                                if (consoleLogs.isNotEmpty()) {
                                    lazyListState.animateScrollToItem(consoleLogs.size - 1)
                                }
                            }
                            LazyColumn(
                                state = lazyListState,
                                modifier = Modifier.fillMaxSize().padding(8.dp),
                                verticalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                items(consoleLogs) { log ->
                                    Text(
                                        text = log,
                                        color = Color(currentTerminalTheme.text),
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 11.sp,
                                        lineHeight = 14.sp
                                    )
                                }
                            }
                        }
                    }
                }

                if (listToShow.isEmpty()) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text("No items found.")
                    }
                } else {
                    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
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
                                }
                            }
                        }
                    }
                }
            }
        }
        return
    }

    Box(modifier = Modifier.fillMaxSize()) {
        val isListEmpty = results.isEmpty() && !isLoading
        Column(
            modifier = Modifier.fillMaxSize().padding(contentPadding).padding(horizontal = 16.dp),
            verticalArrangement = if (isListEmpty) Arrangement.Center else Arrangement.Top,
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
                    selected = false,
                    onClick = { selectedFilter = "History" },
                    label = { Text("History") }
                )
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "Offline" },
                    label = { Text("Offline") }
                )
            }
            
            if (isLoading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else {
                if (results.isEmpty()) {
                    Spacer(modifier = Modifier.fillMaxHeight(0.2f))
                    Icon(
                        painter = androidx.compose.ui.res.painterResource(android.R.drawable.ic_media_play),
                        contentDescription = "YouTube",
                        modifier = Modifier.size(72.dp).padding(bottom = 16.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Text(
                        "YouTube Search",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                    )
                } else {
                    LazyColumn(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(results) { item ->
                            val savedItem = SavedVideo(item.url, item.name, item.uploaderName, item.thumbnails?.firstOrNull()?.url ?: "")
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                onClick = { 
                                    viewModel.addToHistory(savedItem)
                                    onUrlSelected(item.url) 
                                },
                                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
                            ) {
                                Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Box(modifier = Modifier.size(100.dp, 60.dp)) {
                                        AsyncImage(
                                            model = savedItem.thumbUrl,
                                            contentDescription = null,
                                            modifier = Modifier.fillMaxSize(),
                                            contentScale = androidx.compose.ui.layout.ContentScale.Crop
                                        )
                                    }
                                    Spacer(Modifier.width(12.dp))
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(savedItem.title, style = MaterialTheme.typography.titleSmall, maxLines = 2, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold)
                                        Spacer(Modifier.height(4.dp))
                                        Text(savedItem.uploader, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                    }
                                    IconButton(onClick = { 
                                        showDownloadDialog = savedItem
                                    }) {
                                        Icon(Icons.Default.Download, "Download", tint = MaterialTheme.colorScheme.primary)
                                    }
                                }
                            }
                        }
                        item { Spacer(Modifier.height(80.dp)) }
                    }
                }
            }
        }
        
        val lastPlayed = viewModel.lastPlayedUrl.value
        if (lastPlayed != null) {
            ExtendedFloatingActionButton(
                onClick = { onUrlSelected(lastPlayed) },
                modifier = Modifier.align(Alignment.BottomEnd).padding(end = 16.dp, bottom = 16.dp + contentPadding.calculateBottomPadding()),
                containerColor = MaterialTheme.colorScheme.primary,
                icon = { Icon(Icons.Default.PlayArrow, contentDescription = "Continue playing") },
                text = { Text("Continue") },
                shape = RoundedCornerShape(12.dp)
            )
        }

        if (showDownloadDialog != null) {
            AlertDialog(
                onDismissRequest = { showDownloadDialog = null },
                title = { Text("Download Options") },
                text = {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Select Quality:")
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            FilterChip(selected = selectedQuality == "360p", onClick = { selectedQuality = "360p" }, label = { Text("360p") })
                            FilterChip(selected = selectedQuality == "720p", onClick = { selectedQuality = "720p" }, label = { Text("720p") })
                            FilterChip(selected = selectedQuality == "1080p", onClick = { selectedQuality = "1080p" }, label = { Text("1080p") })
                        }
                        Spacer(Modifier.height(8.dp))
                        Text("Format:")
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            FilterChip(selected = !isAudioOnly, onClick = { isAudioOnly = false }, label = { Text("Video") })
                            FilterChip(selected = isAudioOnly, onClick = { isAudioOnly = true }, label = { Text("Audio") })
                        }
                    }
                },
                confirmButton = {
                    TextButton(onClick = {
                        viewModel.startMockDownload(showDownloadDialog!!, selectedQuality, if(isAudioOnly) "audio" else "video", context)
                        selectedFilter = "Offline"
                        showDownloadDialog = null
                    }) { Text("Download") }
                },
                dismissButton = {
                    TextButton(onClick = { showDownloadDialog = null }) { Text("Cancel") }
                }
            )
        }
    }
}
"""

with open(newpipe_path, "w") as f:
    f.write(new_newpipe_tab)

# Update DownloaderViewModel to use DownloadManager
vm_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderViewModel.kt"
with open(vm_path, "r") as f:
    vm_content = f.read()

download_manager_logic = """
    fun startMockDownload(video: SavedVideo, quality: String, format: String, context: Context) {
        viewModelScope.launch(Dispatchers.IO) {
            consoleLogs.add("fookus@tube: ~$ fookus-dl -f $quality $format ${video.url}")
            delay(500)
            consoleLogs.add("[newpipe] Extracting URL: ${video.url}")
            try {
                org.schabi.newpipe.extractor.NewPipe.init(org.schabi.newpipe.extractor.DownloaderImpl.getInstance())
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
                    
                    val request = android.app.DownloadManager.Request(Uri.parse(streamUrl))
                    request.setTitle(video.title)
                    request.setDescription("Downloading via FookusTube")
                    request.setNotificationVisibility(android.app.DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                    val fileName = "${video.title.replace(Regex("[^a-zA-Z0-9.-]"), "_")}.mp4"
                    request.setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS, fileName)
                    
                    val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as android.app.DownloadManager
                    downloadManager.enqueue(request)
                    
                    delay(500)
                    consoleLogs.add("Download queued successfully in Android system!")
                    val savedWithUri = video.copy(localUri = "file:///storage/emulated/0/Download/$fileName")
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
"""

if "org.schabi.newpipe.extractor.DownloaderImpl" not in vm_content:
    vm_content = re.sub(
        r'fun startMockDownload\([\s\S]*?fun addToOffline\(',
        download_manager_logic.strip() + "\n\n    fun addToOffline(",
        vm_content
    )

with open(vm_path, "w") as f:
    f.write(vm_content)

print("Applied separate pages and actual NewPipe downloading logic.")
