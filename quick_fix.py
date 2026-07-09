import re

# Update ChannelScreen.kt
channel_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/ChannelScreen.kt"
with open(channel_path, "r") as f:
    channel_content = f.read()
    
# Replace the ChannelInfo logic with getInitialPage()
extract_old = """                val channelInfo = org.schabi.newpipe.extractor.channel.ChannelInfo.getInfo(url)
                val items = channelInfo.relatedItems.filterIsInstance<StreamInfoItem>()
                withContext(Dispatchers.Main) {
                    channelName = channelInfo.name
                    channelAvatar = channelInfo.avatarUrl
                    channelBanner = channelInfo.bannerUrl
                    subscriberCount = channelInfo.subscriberCount.toString()
                    videos = items"""

extract_new = """                val channelInfo = org.schabi.newpipe.extractor.channel.ChannelInfo.getInfo(url)
                val items = channelInfo.relatedItems.filterIsInstance<StreamInfoItem>()
                withContext(Dispatchers.Main) {
                    channelName = channelInfo.name
                    channelAvatar = channelInfo.avatarUrl
                    channelBanner = channelInfo.bannerUrl
                    subscriberCount = channelInfo.subscriberCount.toString()
                    videos = items"""

# Actually, let's just use getRelatedItems() if it's ListInfo
fixed_extract = """                val channelInfo = org.schabi.newpipe.extractor.channel.ChannelInfo.getInfo(url)
                val items = channelInfo.relatedItems
                withContext(Dispatchers.Main) {
                    channelName = channelInfo.name
                    videos = items.filterIsInstance<StreamInfoItem>()"""

if extract_old in channel_content:
    channel_content = channel_content.replace(extract_old, fixed_extract)
else:
    # Just replace all
    pass

# We will just rewrite ChannelScreen.kt completely
new_channel_screen = """package com.fookus.tube.ui

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
    var videos by remember { mutableStateOf<List<StreamInfoItem>>(emptyList()) }
    
    val scope = rememberCoroutineScope()
    
    LaunchedEffect(url) {
        scope.launch(Dispatchers.IO) {
            try {
                val channelInfo = ChannelInfo.getInfo(url)
                val items = channelInfo.relatedItems.filterIsInstance<StreamInfoItem>()
                withContext(Dispatchers.Main) {
                    channelName = channelInfo.name
                    videos = items
                    isLoading = false
                }
            } catch (e: Exception) {
                try {
                    val extractor = ServiceList.YouTube.getChannelExtractor(url)
                    extractor.fetchPage()
                    val items = extractor.initialPage.items.filterIsInstance<StreamInfoItem>()
                    withContext(Dispatchers.Main) {
                        channelName = extractor.name
                        videos = items
                        isLoading = false
                    }
                } catch(e2: Exception) {
                    e2.printStackTrace()
                    withContext(Dispatchers.Main) {
                        isLoading = false
                    }
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
"""
with open(channel_path, "w") as f:
    f.write(new_channel_screen)

# 2. Fix DownloaderScreen.kt to pass viewModel
ds_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"
with open(ds_path, "r") as f:
    ds_content = f.read()
    
# Replace the entire PlayerScreen call in DownloaderScreen.kt
old_player = """    if (playingUrl != null) {
        PlayerScreen(
            url = playingUrl!!,
            onBack = { playingUrl = null },
            onDownload = { dlUrl ->
                playingUrl = null
            },
            onChannelSelected = { url ->
                channelUrl = url
            }
        )
        return
    }"""
    
new_player = """    if (playingUrl != null) {
        PlayerScreen(
            url = playingUrl!!,
            viewModel = viewModel,
            onBack = { playingUrl = null },
            onDownload = { dlUrl ->
                playingUrl = null
            },
            onChannelSelected = { url ->
                channelUrl = url
            }
        )
        return
    }"""
    
if old_player in ds_content:
    ds_content = ds_content.replace(old_player, new_player)
with open(ds_path, "w") as f:
    f.write(ds_content)

print("Applied quick fix for ChannelScreen and DownloaderScreen")
