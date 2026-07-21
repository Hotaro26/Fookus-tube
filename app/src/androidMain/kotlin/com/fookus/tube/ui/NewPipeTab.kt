package com.fookus.tube.ui

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Bookmarks
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Book
import androidx.compose.material.icons.filled.ContentPaste
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.draw.clip
import androidx.compose.ui.Modifier
import androidx.activity.compose.BackHandler
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.Spring
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.ui.draw.scale
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.interaction.collectIsHoveredAsState
import androidx.compose.foundation.combinedClickable

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

@OptIn(ExperimentalMaterial3Api::class, androidx.compose.foundation.ExperimentalFoundationApi::class)
@Composable
fun NewPipeTab(
    viewModel: DownloaderViewModel,
    contentPadding: PaddingValues,
    onUrlSelected: (String) -> Unit,
    onChannelSelected: (String) -> Unit = {}
) {
    var query by viewModel.newPipeQuery
    var results by viewModel.newPipeResults
    var isLoading by remember { mutableStateOf(false) }
    var searchJob by remember { mutableStateOf<kotlinx.coroutines.Job?>(null) }

    var channelPopupItem by remember { mutableStateOf<StreamInfoItem?>(null) }
    var currentExtractor by remember { mutableStateOf<org.schabi.newpipe.extractor.search.SearchExtractor?>(null) }
    var currentPage by remember { mutableStateOf<org.schabi.newpipe.extractor.ListExtractor.InfoItemsPage<org.schabi.newpipe.extractor.InfoItem>?>(null) }
    var isLoadingMore by remember { mutableStateOf(false) }
    val listState = androidx.compose.foundation.lazy.grid.rememberLazyGridState()

    val endOfListReached by remember {
        androidx.compose.runtime.derivedStateOf {
            val lastVisibleItem = listState.layoutInfo.visibleItemsInfo.lastOrNull()
            lastVisibleItem != null && lastVisibleItem.index >= results.size - 2
        }
    }

    LaunchedEffect(endOfListReached) {
        if (endOfListReached && !isLoadingMore && !isLoading && currentPage?.hasNextPage() == true) {
            isLoadingMore = true
            withContext(Dispatchers.IO) {
                try {
                    val nextPage = currentExtractor!!.getPage(currentPage!!.nextPage)
                    val items = nextPage.items.filterIsInstance<StreamInfoItem>()
                    withContext(Dispatchers.Main) {
                        results = results + items
                        currentPage = nextPage
                    }
                } catch(e: Exception) { e.printStackTrace() }
                withContext(Dispatchers.Main) { isLoadingMore = false }
            }
        }
    }
    val selectedFilter = viewModel.activeFilter.value
    val setSelectedFilter = { filter: String -> viewModel.activeFilter.value = filter } // "Search", "History", "Offline"
    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current

    val history by viewModel.history
    var showDownloadDialog by remember { mutableStateOf<SavedVideo?>(null) }
    var videoToDelete by remember { mutableStateOf<Pair<SavedVideo, String>?>(null) }
    var showCreatePlaylistDialog by remember { mutableStateOf(false) }
    var showDownloadedScreen by remember { mutableStateOf(false) }
    var newPlaylistName by remember { mutableStateOf("") }
    var selectedQuality by remember { mutableStateOf("720p") }
    var isAudioOnly by remember { mutableStateOf(false) }
    val offline by viewModel.offline

    val keyboardController = androidx.compose.ui.platform.LocalSoftwareKeyboardController.current
    val focusManager = androidx.compose.ui.platform.LocalFocusManager.current

    val performSearch = {
        keyboardController?.hide()
        focusManager.clearFocus()
        if (query.isNotBlank()) {
            setSelectedFilter("Search")
            isLoading = true
            searchJob?.cancel()
            searchJob = coroutineScope.launch(Dispatchers.IO) {
                try {
                    val service = when (viewModel.searchSource.value) {
                        "PeerTube" -> ServiceList.PeerTube
                        "SoundCloud" -> ServiceList.SoundCloud
                        else -> ServiceList.YouTube
                    }
                    val searchExtractor = service.getSearchExtractor(query)
                    searchExtractor.fetchPage()
                    val items = searchExtractor.initialPage.items.filterIsInstance<StreamInfoItem>()
                    withContext(Dispatchers.Main) {
                        results = items
                        currentExtractor = searchExtractor
                        currentPage = searchExtractor.initialPage
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

    androidx.compose.animation.AnimatedContent(targetState = selectedFilter, label = "filter_transition") { currentFilter ->
        if (currentFilter != "Search") {
            BackHandler {
                if (currentFilter.startsWith("Bookmark:")) {
                    setSelectedFilter("Bookmarks")
                } else {
                    setSelectedFilter("Search")
                }
            }

        // Separate Page for History or Offline
        Scaffold(
            topBar = {
                TopAppBar(
                    title = { Text(currentFilter) },
                    navigationIcon = {
                        IconButton(onClick = { setSelectedFilter("Search") }) {
                            Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                        }
                    }
                )
            },
            floatingActionButton = {
                if (currentFilter == "Bookmarks") {
                    FloatingActionButton(onClick = { showCreatePlaylistDialog = true }) {
                        Icon(Icons.Default.Add, contentDescription = "Add Playlist")
                    }
                } else if (currentFilter == "Offline") {
                    FloatingActionButton(onClick = { showDownloadedScreen = true }) {
                        Icon(androidx.compose.material.icons.Icons.Default.Book, contentDescription = "Downloaded Videos")
                    }
                }
            },
            modifier = Modifier.padding(bottom = contentPadding.calculateBottomPadding())
        ) { innerPadding ->
            val listToShow = when {
                    currentFilter == "History" -> history
                    currentFilter == "Offline" -> emptyList()
                    currentFilter.startsWith("Bookmark:") -> {
                        val playlistName = currentFilter.removePrefix("Bookmark: ")
                        viewModel.bookmarks.value[playlistName] ?: emptyList()
                    }
                    else -> emptyList()
                }
            Column(modifier = Modifier.padding(innerPadding).padding(horizontal = 16.dp).fillMaxSize()) {

                if (currentFilter == "Bookmarks") {
                    LazyColumn(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(viewModel.bookmarks.value.keys.toList()) { playlistName ->
                            Card(
                                modifier = Modifier.fillMaxWidth().clickable { setSelectedFilter("Bookmark: $playlistName") },
                                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
                            ) {
                                Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Icon(androidx.compose.material.icons.Icons.Default.Bookmarks, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                                    Spacer(Modifier.width(16.dp))
                                    Column {
                                        Text(playlistName, style = MaterialTheme.typography.titleMedium, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold)
                                        Text("${viewModel.bookmarks.value[playlistName]?.size ?: 0} videos", style = MaterialTheme.typography.bodySmall)
                                    }
                                }
                            }
                        }
                    }
                }
                
                if (currentFilter == "Offline") {
                    var qualityExpanded by remember { mutableStateOf(false) }
                    var modeExpanded by remember { mutableStateOf(false) }
                    var currentQuality by remember { mutableStateOf("720p") }
                    var currentFormat by remember { mutableStateOf("video") }
                    
                    val preview by remember { viewModel.previewMetadata }
                    
                    LaunchedEffect(viewModel.offlineUrl.value) {
                        if (viewModel.offlineUrl.value.isNotBlank() && viewModel.offlineUrl.value.startsWith("http")) {
                            kotlinx.coroutines.delay(1000)
                            viewModel.fetchPreview(viewModel.offlineUrl.value)
                        } else {
                            viewModel.previewMetadata.value = null
                        }
                    }
                    

                    
                    LaunchedEffect(viewModel.triggerDownloadUrl.value) {
                        if (viewModel.triggerDownloadUrl.value != null) {
                            showDownloadDialog = SavedVideo(viewModel.triggerDownloadUrl.value!!, "Video", "", "")
                            viewModel.triggerDownloadUrl.value = null
                        }
                    }
                    
        OutlinedTextField(
                        value = viewModel.offlineUrl.value,
                        onValueChange = { viewModel.offlineUrl.value = it },
                        placeholder = { Text("Paste YouTube URL here") },
                        modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
                        trailingIcon = {
                            Row {
                                if (viewModel.offlineUrl.value.isNotEmpty()) {
                                    IconButton(onClick = { viewModel.offlineUrl.value = "" }) {
                                        Icon(Icons.Default.Close, contentDescription = "Clear")
                                    }
                                }
                                    val clipboardManager = androidx.compose.ui.platform.LocalClipboardManager.current
                                    IconButton(onClick = { 
                                        clipboardManager.getText()?.let { 
                                            viewModel.offlineUrl.value = it.text
                                        }
                                }) {
                                    Icon(androidx.compose.material.icons.Icons.Default.ContentPaste, "Paste")
                                }
                            }
                        },
                        shape = MaterialTheme.shapes.large
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        ExposedDropdownMenuBox(
                            expanded = qualityExpanded,
                            onExpandedChange = { qualityExpanded = it },
                            modifier = Modifier.weight(1f)
                        ) {
                OutlinedTextField(
                                value = currentQuality,
                                onValueChange = {},
                                readOnly = true,
                                label = { Text("Quality") },
                                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = qualityExpanded) },
                                modifier = Modifier.menuAnchor(),
                                shape = RoundedCornerShape(12.dp)
                            )
                            ExposedDropdownMenu(
                                expanded = qualityExpanded,
                                onDismissRequest = { qualityExpanded = false }
                            ) {
                                val options = if (currentFormat == "audio") {
                                    listOf("Medium", "High", "Best")
                                } else {
                                    val avQuals = preview?.availableQualities
                                    if (!avQuals.isNullOrEmpty()) {
                                        avQuals
                                    } else {
                                        listOf("360p", "720p", "1080p")
                                    }
                                }
                                options.forEach { selectionOption ->
                                    DropdownMenuItem(
                                        text = { Text(selectionOption) },
                                        onClick = {
                                            currentQuality = selectionOption
                                            qualityExpanded = false
                                        }
                                    )
                                }
                            }
                        }
                        
                        ExposedDropdownMenuBox(
                            expanded = modeExpanded,
                            onExpandedChange = { modeExpanded = it },
                            modifier = Modifier.weight(1f)
                        ) {
                OutlinedTextField(
                                value = currentFormat,
                                onValueChange = {},
                                readOnly = true,
                                label = { Text("Format") },
                                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = modeExpanded) },
                                modifier = Modifier.menuAnchor(),
                                shape = RoundedCornerShape(12.dp)
                            )
                            ExposedDropdownMenu(
                                expanded = modeExpanded,
                                onDismissRequest = { modeExpanded = false }
                            ) {
                                listOf("video", "audio").forEach { selectionOption ->
                                    DropdownMenuItem(
                                        text = { Text(selectionOption) },
                                        onClick = {
                                            currentFormat = selectionOption
                                            modeExpanded = false
                                        }
                                    )
                                }
                            }
                        }
                    }
                    
                    preview?.let { meta ->
                        Card(
                            modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
                            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)),
                            shape = RoundedCornerShape(16.dp)
                        ) {
                            Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                                if (meta.thumbUrl.isNotEmpty()) {
                                    AsyncImage(
                                        model = meta.thumbUrl,
                                        contentDescription = null,
                                        modifier = Modifier.size(80.dp, 48.dp).clip(RoundedCornerShape(8.dp)),
                                        contentScale = androidx.compose.ui.layout.ContentScale.Crop
                                    )
                                    Spacer(Modifier.width(12.dp))
                                }
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = meta.title,
                                        style = MaterialTheme.typography.titleSmall,
                                        maxLines = 1,
                                        overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis,
                                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                                    )
                                    Spacer(Modifier.height(4.dp))
                                    Text(
                                        text = meta.author,
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                                if (viewModel.activeDownloads.contains(viewModel.offlineUrl.value)) {
                                    IconButton(onClick = { viewModel.cancelDownload(viewModel.offlineUrl.value) }) {
                                        Icon(Icons.Default.Close, contentDescription = "Cancel Download", tint = MaterialTheme.colorScheme.error)
                                    }
                                }
                            }
                        }
                    }

                    val isDownloading = viewModel.activeDownloads.contains(viewModel.offlineUrl.value)
                    Button(
                        onClick = {
                            if (!isDownloading && viewModel.offlineUrl.value.isNotBlank()) {
                                val title = preview?.title ?: "Manual Download"
                                val author = preview?.author ?: "Unknown"
                                val thumb = preview?.thumbUrl ?: ""
                                val savedItem = SavedVideo(viewModel.offlineUrl.value, title, author, thumb)
                                viewModel.startMockDownload(savedItem, currentQuality, currentFormat, context)
                            }
                        },
                        modifier = Modifier.fillMaxWidth().height(56.dp).padding(bottom = 16.dp),
                        shape = RoundedCornerShape(16.dp),
                        enabled = !isDownloading
                    ) {
                        if (isDownloading) {
                            androidx.compose.material3.CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = MaterialTheme.colorScheme.onPrimary,
                                strokeWidth = 2.dp
                            )
                            Spacer(Modifier.width(12.dp))
                            Text("Downloading...")
                        } else {
                            Icon(Icons.Default.Download, null)
                            Spacer(Modifier.width(8.dp))
                            Text("Download")
                        }
                    }
                    
                    val currentTerminalTheme = viewModel.terminalTheme.value
                    val consoleLogs = viewModel.consoleLogs
                    var showFullscreenLogs by viewModel.showFullscreenLogs

                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(180.dp)
                            .padding(bottom = 16.dp)
                            .pointerInput(Unit) {
                                detectTapGestures(
                                    onDoubleTap = { showFullscreenLogs = true }
                                )
                            },
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

                    if (showFullscreenLogs) {
                        androidx.compose.ui.window.Dialog(
                            onDismissRequest = { showFullscreenLogs = false },
                            properties = androidx.compose.ui.window.DialogProperties(
                                usePlatformDefaultWidth = false
                            )
                        ) {
                            Surface(
                                modifier = Modifier.fillMaxSize(),
                                color = Color(currentTerminalTheme.background)
                            ) {
                                Column(modifier = Modifier.fillMaxSize()) {
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .background(Color(currentTerminalTheme.header))
                                            .statusBarsPadding()
                                            .padding(horizontal = 16.dp, vertical = 12.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        IconButton(onClick = { showFullscreenLogs = false }) {
                                            Icon(
                                                imageVector = Icons.Default.ArrowBack,
                                                contentDescription = "Back",
                                                tint = Color(currentTerminalTheme.text)
                                            )
                                        }
                                        Spacer(Modifier.width(8.dp))
                                        Text(
                                            text = "Terminal Logs",
                                            color = Color(currentTerminalTheme.text),
                                            style = MaterialTheme.typography.titleMedium,
                                            fontFamily = FontFamily.Monospace
                                        )
                                        Spacer(Modifier.weight(1f))
                                        IconButton(onClick = { viewModel.clearConsole() }) {
                                            Icon(
                                                imageVector = Icons.Default.Delete,
                                                contentDescription = "Clear",
                                                tint = Color(currentTerminalTheme.text).copy(alpha = 0.8f)
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
                                        modifier = Modifier.fillMaxSize().padding(16.dp),
                                        verticalArrangement = Arrangement.spacedBy(6.dp)
                                    ) {
                                        items(consoleLogs) { log ->
                                            Text(
                                                text = log,
                                                color = Color(currentTerminalTheme.text),
                                                fontFamily = FontFamily.Monospace,
                                                fontSize = 12.sp,
                                                lineHeight = 16.sp
                                            )
                                        }
                                    }
                                }
                            }
                            BackHandler {
                                showFullscreenLogs = false
                            }
                        }
                    }
                }

                if (currentFilter != "Offline" && listToShow.isEmpty()) {
                    Box(modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)), contentAlignment = Alignment.Center) {
                        Text("No items found.")
                    }
                } else if (currentFilter != "Offline") {
                    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(listToShow, key = { it.url + currentFilter }) { item ->
                            val dismissState = androidx.compose.material3.rememberSwipeToDismissBoxState(
                                confirmValueChange = {
                                    if (it == androidx.compose.material3.SwipeToDismissBoxValue.EndToStart || it == androidx.compose.material3.SwipeToDismissBoxValue.StartToEnd) {
                                        videoToDelete = Pair(item, currentFilter)
                                        false
                                    } else false
                                }
                            )

                            androidx.compose.material3.SwipeToDismissBox(
                                state = dismissState,
                                backgroundContent = {
                                    Box(
                                        Modifier
                                            .fillMaxSize()
                                            .clip(RoundedCornerShape(12.dp))
                                            .background(MaterialTheme.colorScheme.errorContainer)
                                            .padding(horizontal = 20.dp),
                                        contentAlignment = Alignment.CenterEnd
                                    ) {
                                        Icon(
                                            Icons.Default.Delete,
                                            contentDescription = "Delete",
                                            tint = MaterialTheme.colorScheme.onErrorContainer
                                        )
                                    }
                                }
                            ) {
                                Card(
                                    modifier = Modifier.fillMaxWidth().combinedClickable(
                                        onClick = { 
                                            viewModel.addToHistory(item)
                                            onUrlSelected(item.url) 
                                        },
                                        onLongClick = {
                                            if (currentFilter == "History") viewModel.removeFromHistory(item)
                                            else videoToDelete = Pair(item, currentFilter)
                                        }
                                    ),
                                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 1f)),
                                    shape = RoundedCornerShape(12.dp)
                                ) {
                                    Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                        Box(modifier = Modifier.size(100.dp, 60.dp)) {
                                            AsyncImage(
                                                model = item.localThumbUri ?: item.thumbUrl,
                                                contentDescription = null,
                                                modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)),
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
        }
        } else {
            BackHandler(enabled = query.isNotEmpty() || results.isNotEmpty()) {
                searchJob?.cancel()
                isLoading = false
                query = ""
                results = emptyList()
                currentExtractor = null
                currentPage = null
            }
            Box(modifier = Modifier.fillMaxSize()) {

        val isListEmpty = results.isEmpty() && !isLoading
        Column(
            modifier = Modifier.fillMaxSize().padding(contentPadding).padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.Top,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            AnimatedVisibility(
                visible = isListEmpty,
                enter = fadeIn() + expandVertically(expandFrom = Alignment.Top),
                exit = fadeOut() + shrinkVertically(shrinkTowards = Alignment.Top)
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Spacer(modifier = Modifier.height(100.dp))
                    Box(
                        modifier = Modifier
                            .size(72.dp)
                            .padding(bottom = 16.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f))
                            .border(1.dp, MaterialTheme.colorScheme.primary, RoundedCornerShape(12.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = androidx.compose.material.icons.Icons.Default.PlayArrow,
                            contentDescription = "Fookus Tube",
                            modifier = Modifier.size(36.dp),
                            tint = MaterialTheme.colorScheme.primary
                        )
                    }
                    Text(
                        "Fookus Tube",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(24.dp))
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth().padding(top = 16.dp, bottom = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                AnimatedVisibility(visible = results.isNotEmpty() || isLoading) {
                    IconButton(
                        onClick = { 
                            searchJob?.cancel()
                            isLoading = false
                            query = ""
                            results = emptyList()
                            currentExtractor = null
                            currentPage = null
                            focusManager.clearFocus() 
                        },
                        modifier = Modifier.padding(end = 8.dp).background(MaterialTheme.colorScheme.surfaceVariant, androidx.compose.foundation.shape.CircleShape)
                    ) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }

                OutlinedTextField(
                    value = query,
                    onValueChange = { query = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Search YouTube...") },
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                    keyboardActions = KeyboardActions(onSearch = { performSearch() }),
                    trailingIcon = {
                        if (query.isNotEmpty()) {
                            IconButton(onClick = { 
                                searchJob?.cancel()
                                isLoading = false
                                query = ""
                                results = emptyList()
                                currentExtractor = null
                                currentPage = null
                                focusManager.clearFocus()
                                keyboardController?.hide()
                            }) {
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
            }
            
            AnimatedVisibility(visible = isListEmpty) {
                @OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
                androidx.compose.foundation.layout.FlowRow(
                    modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(0.dp)
                ) {
                    @Composable
                    fun AnimatedFilterChip(label: String, onClick: () -> Unit) {
                        val interactionSource = androidx.compose.runtime.remember { androidx.compose.foundation.interaction.MutableInteractionSource() }
                        val isPressed by interactionSource.collectIsPressedAsState()
                        val cornerRadius by androidx.compose.animation.core.animateDpAsState(targetValue = if (isPressed) 50.dp else 8.dp)
                        
                        FilterChip(
                            selected = false,
                            onClick = onClick,
                            label = { Text(label) },
                            shape = RoundedCornerShape(cornerRadius),
                            interactionSource = interactionSource
                        )
                    }
    
                    AnimatedFilterChip("History") { setSelectedFilter("History") }
                    AnimatedFilterChip("Offline") { setSelectedFilter("Offline") }
                    AnimatedFilterChip("Bookmarks") { setSelectedFilter("Bookmarks") }
                    AnimatedFilterChip("Downloads") { showDownloadedScreen = true }
                }
            }
            
            if (isLoading) {
                Box(modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else {
                if (results.isEmpty()) {
                    // Empty state handled above
                } else {
                    LazyVerticalGrid(state = listState, columns = GridCells.Adaptive(minSize = 350.dp), modifier = Modifier.weight(1f).clip(RoundedCornerShape(8.dp)), verticalArrangement = Arrangement.spacedBy(8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(results) { item ->
                            val savedItem = SavedVideo(item.url, item.name, item.uploaderName, item.thumbnails?.firstOrNull()?.url ?: "")
                            Card(
                                modifier = Modifier.fillMaxWidth().combinedClickable(
                                    onClick = { 
                                        viewModel.addToHistory(savedItem)
                                        onUrlSelected(item.url) 
                                    },
                                    onLongClick = {
                                        channelPopupItem = item
                                    }
                                ),
                                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
                            ) {
                                Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Box(modifier = Modifier.size(100.dp, 60.dp)) {
                                        AsyncImage(
                                            model = savedItem.thumbUrl,
                                            contentDescription = null,
                                            modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)),
                                            contentScale = androidx.compose.ui.layout.ContentScale.Crop
                                        )
                                    }
                                    Spacer(Modifier.width(12.dp))
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(savedItem.title, style = MaterialTheme.typography.titleSmall, maxLines = 2, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold)
                                        Spacer(Modifier.height(4.dp))
                                        Text(savedItem.uploader, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                    }
                                }
                            }
                        }
                        item { Spacer(Modifier.height(80.dp)) }
                    }
                }
            }
        }
        
        Column(
            modifier = Modifier.align(Alignment.BottomEnd).padding(end = 16.dp, bottom = 16.dp + contentPadding.calculateBottomPadding()),
            horizontalAlignment = Alignment.End,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            val context = LocalContext.current
            val clipboardManager = androidx.compose.ui.platform.LocalClipboardManager.current
            
            FloatingActionButton(
                onClick = {
                    val clipboardText = clipboardManager.getText()?.text
                    if (clipboardText != null && (clipboardText.contains("youtube.com") || clipboardText.contains("youtu.be"))) {
                        onUrlSelected(clipboardText)
                    } else {
                        Toast.makeText(context, "Not a YouTube link! Please try with a valid link.", Toast.LENGTH_SHORT).show()
                    }
                },
                shape = CircleShape,
                containerColor = MaterialTheme.colorScheme.secondaryContainer
            ) {
                Icon(Icons.Default.ContentPaste, contentDescription = "Paste YouTube Link")
            }

            val lastPlayed = viewModel.lastPlayedUrl.value
            if (lastPlayed != null) {
                val fabInteraction = remember { MutableInteractionSource() }
                val fabPressed by fabInteraction.collectIsPressedAsState()
                val fabHovered by fabInteraction.collectIsHoveredAsState()
                val isFabActive = fabPressed || fabHovered
                val animatedRadius by animateDpAsState(targetValue = if (isFabActive) 50.dp else 12.dp, animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy))

                ExtendedFloatingActionButton(
                    onClick = { onUrlSelected(lastPlayed) },
                    containerColor = MaterialTheme.colorScheme.primary,
                    icon = { Icon(Icons.Default.PlayArrow, contentDescription = "Continue playing") },
                    text = { Text("Continue") },
                    shape = RoundedCornerShape(animatedRadius),
                    interactionSource = fabInteraction
                )
            }
        }

    }
        }
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
                    viewModel.offlineUrl.value = showDownloadDialog!!.url
                    viewModel.startMockDownload(showDownloadDialog!!, selectedQuality, if(isAudioOnly) "audio" else "video", context)
                    setSelectedFilter("Offline")
                    showDownloadDialog = null
                }) { Text("Download") }
            },
            dismissButton = {
                TextButton(onClick = { showDownloadDialog = null }) { Text("Cancel") }
            }
        )
    }

    if (videoToDelete != null) {
        val (video, filterContext) = videoToDelete!!
        AlertDialog(
            onDismissRequest = { videoToDelete = null },
            title = { Text(if (filterContext == "History") "Clear History" else "Delete Video") },
            text = { 
                Text(
                    if (filterContext == "History") "Are you sure you want to clear '${video.title}' from your watch history?"
                    else "Are you sure you want to remove '${video.title}'?"
                ) 
            },
            confirmButton = {
                TextButton(onClick = {
                    if (filterContext == "History") viewModel.removeFromHistory(video)
                    else if (filterContext == "Offline") viewModel.removeFromOffline(video)
                    else if (filterContext.startsWith("Bookmark:")) {
                        val playlistName = filterContext.removePrefix("Bookmark: ")
                        viewModel.removeVideoFromBookmark(playlistName, video.url)
                    }
                    videoToDelete = null
                }) {
                    Text(if (filterContext == "History") "Clear" else "Delete", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = { videoToDelete = null }) {
                    Text("Cancel")
                }
            }
        )
    }

    if (showDownloadedScreen) {
        androidx.compose.ui.window.Dialog(
            onDismissRequest = { showDownloadedScreen = false },
            properties = androidx.compose.ui.window.DialogProperties(
                usePlatformDefaultWidth = false
            )
        ) {
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = MaterialTheme.colorScheme.background
            ) {
                Column(modifier = Modifier.fillMaxSize()) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .statusBarsPadding()
                            .padding(horizontal = 16.dp, vertical = 12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        IconButton(onClick = { showDownloadedScreen = false }) {
                            Icon(
                                imageVector = androidx.compose.material.icons.Icons.Default.ArrowBack,
                                contentDescription = "Back",
                                tint = MaterialTheme.colorScheme.onBackground
                            )
                        }
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = "Downloaded Videos",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }
                    HorizontalDivider()
                    
                    val downloadedList = offline
                    if (downloadedList.isEmpty()) {
                        Box(
                            modifier = Modifier.fillMaxSize(),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                "No downloaded videos found.",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize().padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(downloadedList, key = { it.url }) { item ->
                                val dismissState = androidx.compose.material3.rememberSwipeToDismissBoxState(
                                    confirmValueChange = {
                                        if (it == androidx.compose.material3.SwipeToDismissBoxValue.EndToStart || it == androidx.compose.material3.SwipeToDismissBoxValue.StartToEnd) {
                                            videoToDelete = Pair(item, "Offline")
                                            false
                                        } else false
                                    }
                                )

                                androidx.compose.material3.SwipeToDismissBox(
                                    state = dismissState,
                                    backgroundContent = {
                                        Box(
                                            Modifier
                                                .fillMaxSize()
                                                .clip(RoundedCornerShape(12.dp))
                                                .background(MaterialTheme.colorScheme.errorContainer)
                                                .padding(horizontal = 20.dp),
                                            contentAlignment = Alignment.CenterEnd
                                        ) {
                                            Icon(
                                                androidx.compose.material.icons.Icons.Default.Delete,
                                                contentDescription = "Delete",
                                                tint = MaterialTheme.colorScheme.onErrorContainer
                                            )
                                        }
                                    }
                                ) {
                                    Card(
                                        modifier = Modifier.fillMaxWidth().combinedClickable(
                                            onClick = { 
                                                viewModel.addToHistory(item)
                                                onUrlSelected(item.url)
                                                showDownloadedScreen = false
                                            },
                                            onLongClick = {
                                                videoToDelete = Pair(item, "Offline")
                                            }
                                        ),
                                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 1f)),
                                        shape = RoundedCornerShape(12.dp)
                                    ) {
                                        Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                            Box(modifier = Modifier.size(100.dp, 60.dp)) {
                                                AsyncImage(
                                                    model = item.localThumbUri ?: item.thumbUrl,
                                                    contentDescription = null,
                                                    modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)),
                                                    contentScale = androidx.compose.ui.layout.ContentScale.Crop
                                                )
                                            }
                                            Spacer(Modifier.width(12.dp))
                                            Column(modifier = Modifier.weight(1f)) {
                                                Text(
                                                    text = item.title,
                                                    style = MaterialTheme.typography.titleSmall,
                                                    maxLines = 2,
                                                    fontWeight = androidx.compose.ui.text.font.FontWeight.Bold,
                                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                                )
                                                Spacer(Modifier.height(4.dp))
                                                Text(
                                                    text = item.uploader,
                                                    style = MaterialTheme.typography.bodySmall,
                                                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f)
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            BackHandler {
                showDownloadedScreen = false
            }
        }
    }

    if (showCreatePlaylistDialog) {
        AlertDialog(
            onDismissRequest = { 
                showCreatePlaylistDialog = false
                newPlaylistName = ""
            },
            title = { Text("New Playlist") },
            text = {
                OutlinedTextField(
                    value = newPlaylistName,
                    onValueChange = { newPlaylistName = it },
                    label = { Text("Playlist Name") },
                    singleLine = true
                )
            },
            confirmButton = {
                TextButton(onClick = {
                    if (newPlaylistName.isNotBlank()) {
                        viewModel.addBookmarkPlaylist(newPlaylistName.trim())
                    }
                    showCreatePlaylistDialog = false
                    newPlaylistName = ""
                }) {
                    Text("Create")
                }
            },
            dismissButton = {
                TextButton(onClick = { 
                    showCreatePlaylistDialog = false
                    newPlaylistName = ""
                }) {
                    Text("Cancel")
                }
            }
        )
    }

    val audioSelectionRequired by viewModel.audioSelectionRequired.collectAsState()
    
    val currentAudioSelection = audioSelectionRequired
    if (currentAudioSelection != null) {
        AlertDialog(
            onDismissRequest = { viewModel.selectedAudioStream.value = currentAudioSelection.first() },
            title = { Text("Select Audio Track") },
            text = {
                LazyColumn(modifier = Modifier.fillMaxWidth().heightIn(max = 300.dp)) {
                    items(currentAudioSelection) { stream ->
                        val lang = stream.audioLocale?.displayName ?: "Original"
                        Card(
                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp).clickable {
                                viewModel.selectedAudioStream.value = stream
                            },
                            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                        ) {
                            Text(
                                text = lang,
                                modifier = Modifier.padding(16.dp),
                                style = MaterialTheme.typography.bodyLarge
                            )
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { viewModel.selectedAudioStream.value = currentAudioSelection.first() }) {
                    Text("Skip (Original)")
                }
            }
        )
    }
}
