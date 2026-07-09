package com.fookus.tube.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.activity.compose.BackHandler
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.schabi.newpipe.extractor.ServiceList
import org.schabi.newpipe.extractor.channel.ChannelInfo
import org.schabi.newpipe.extractor.stream.StreamInfoItem

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChannelScreen(
    url: String,
    onBack: () -> Unit,
    onVideoSelected: (String) -> Unit
) {
    var isLoading by remember { mutableStateOf(true) }
    var channelName by remember { mutableStateOf("") }
    var channelAvatar by remember { mutableStateOf<String?>(null) }
    var channelBanner by remember { mutableStateOf<String?>(null) }
    var subscriberCount by remember { mutableStateOf("") }
    var videos by remember { mutableStateOf<List<StreamInfoItem>>(emptyList()) }
    
    val scope = rememberCoroutineScope()
    
    BackHandler {
        onBack()
    }
    
    LaunchedEffect(url) {
        scope.launch(Dispatchers.IO) {
            try {
                val channelInfo = ChannelInfo.getInfo(url)
                val tabs = channelInfo.tabs
                val tabInfo = org.schabi.newpipe.extractor.channel.tabs.ChannelTabInfo.getInfo(ServiceList.YouTube, tabs.first())
                val items = tabInfo.relatedItems.filterIsInstance<StreamInfoItem>()
                withContext(Dispatchers.Main) {
                    channelName = channelInfo.name
                    channelAvatar = channelInfo.avatars?.firstOrNull()?.url
                    channelBanner = channelInfo.banners?.firstOrNull()?.url
                    subscriberCount = channelInfo.subscriberCount.toString()
                    videos = items
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
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(channelName.ifEmpty { "Channel" }) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier.padding(padding).fillMaxSize().padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                                item {
                    if (channelBanner != null) {
                        AsyncImage(
                            model = channelBanner,
                            contentDescription = "Banner",
                            modifier = Modifier.fillMaxWidth().height(120.dp).clip(RoundedCornerShape(12.dp)),
                            contentScale = ContentScale.Crop
                        )
                    }
                    Spacer(Modifier.height(16.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        if (channelAvatar != null) {
                            AsyncImage(
                                model = channelAvatar,
                                contentDescription = "Avatar",
                                modifier = Modifier.size(64.dp).clip(CircleShape),
                                contentScale = ContentScale.Crop
                            )
                            Spacer(Modifier.width(16.dp))
                        }
                        Column {
                            Text(channelName, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                            if (subscriberCount.isNotBlank() && subscriberCount != "-1") {
                                Text("$subscriberCount subscribers", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                        }
                    }
                    Spacer(Modifier.height(16.dp))
                    Divider()
                }
                
                items(videos) { item ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        onClick = { onVideoSelected(item.url) },
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
                    ) {
                        Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                            Box(modifier = Modifier.size(120.dp, 72.dp)) {
                                AsyncImage(
                                    model = item.thumbnails?.firstOrNull()?.url ?: "",
                                    contentDescription = null,
                                    modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)),
                                    contentScale = ContentScale.Crop
                                )
                            }
                            Spacer(Modifier.width(12.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(item.name, style = MaterialTheme.typography.titleSmall, maxLines = 2, fontWeight = FontWeight.Bold)
                                Spacer(Modifier.height(4.dp))
                                Text(item.uploaderName, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                        }
                    }
                }
            }
        }
    }
}
