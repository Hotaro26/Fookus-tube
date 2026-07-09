import re

# 1. Update DownloaderScreen.kt to pass viewModel to PlayerScreen
ds_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"
with open(ds_path, "r") as f:
    ds_content = f.read()

if "viewModel = viewModel," not in ds_content and "url = playingUrl!!" in ds_content:
    ds_content = ds_content.replace(
        "url = playingUrl!!,", 
        "url = playingUrl!!,\n            viewModel = viewModel,"
    )
    with open(ds_path, "w") as f:
        f.write(ds_content)

# 2. Update PlayerScreen.kt
player_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/PlayerScreen.kt"
with open(player_path, "r") as f:
    player_content = f.read()

# Add viewModel to PlayerScreen parameters
if "viewModel: DownloaderViewModel" not in player_content:
    player_content = player_content.replace(
        "fun PlayerScreen(url: String, onBack: () -> Unit, onDownload: (String) -> Unit) {",
        "fun PlayerScreen(url: String, viewModel: DownloaderViewModel, onBack: () -> Unit, onDownload: (String) -> Unit) {"
    )
    
# Add Bookmark logic inside PlayerScreen
dialog_code = """    var showBookmarkDialog by remember { mutableStateOf(false) }
    var newPlaylistName by remember { mutableStateOf("") }
    var showNewPlaylistInput by remember { mutableStateOf(false) }

    if (showBookmarkDialog && streamInfo != null) {
        val video = com.fookus.tube.model.SavedVideo(url, streamInfo!!.name, streamInfo!!.uploaderName, streamInfo!!.thumbnails?.firstOrNull()?.url ?: "")
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { showBookmarkDialog = false; showNewPlaylistInput = false; newPlaylistName = "" },
            title = { androidx.compose.material3.Text("Save to Bookmark") },
            text = {
                androidx.compose.foundation.layout.Column {
                    androidx.compose.foundation.lazy.LazyColumn {
                        items(viewModel.bookmarks.value.keys.toList()) { playlist ->
                            androidx.compose.material3.TextButton(
                                onClick = { 
                                    viewModel.addVideoToBookmark(playlist, video)
                                    showBookmarkDialog = false
                                },
                                modifier = androidx.compose.ui.Modifier.fillMaxWidth()
                            ) {
                                androidx.compose.material3.Text(playlist)
                            }
                        }
                    }
                    if (showNewPlaylistInput) {
                        androidx.compose.material3.OutlinedTextField(
                            value = newPlaylistName,
                            onValueChange = { newPlaylistName = it },
                            label = { androidx.compose.material3.Text("New Playlist Name") },
                            singleLine = true
                        )
                        androidx.compose.material3.Button(onClick = {
                            if (newPlaylistName.isNotBlank()) {
                                viewModel.addBookmarkPlaylist(newPlaylistName)
                                viewModel.addVideoToBookmark(newPlaylistName, video)
                                showBookmarkDialog = false
                                showNewPlaylistInput = false
                                newPlaylistName = ""
                            }
                        }) {
                            androidx.compose.material3.Text("Create & Save")
                        }
                    } else {
                        androidx.compose.material3.TextButton(onClick = { showNewPlaylistInput = true }) {
                            androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Add, contentDescription = null)
                            Spacer(androidx.compose.ui.Modifier.width(8.dp))
                            androidx.compose.material3.Text("New Playlist")
                        }
                    }
                }
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { showBookmarkDialog = false }) {
                    androidx.compose.material3.Text("Close")
                }
            }
        )
    }
"""

if "var showBookmarkDialog" not in player_content:
    player_content = player_content.replace("    var selectedFormat by remember { mutableStateOf<org.schabi.newpipe.extractor.stream.VideoStream?>(null) }", "    var selectedFormat by remember { mutableStateOf<org.schabi.newpipe.extractor.stream.VideoStream?>(null) }\n" + dialog_code)

# Add Star icon button in PlayerScreen
if "Icons.Default.Star" not in player_content:
    # Add star icon next to the "Download" button or next to title. Let's add it next to title.
    # The title is: `Text(info.name, style = MaterialTheme.typography.titleLarge...)`
    title_code = 'Text(info.name, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)'
    new_title_code = """Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                            Text(info.name, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                            IconButton(onClick = { showBookmarkDialog = true }) {
                                Icon(androidx.compose.material.icons.Icons.Default.Star, contentDescription = "Bookmark", tint = MaterialTheme.colorScheme.primary)
                            }
                        }"""
    player_content = player_content.replace(title_code, new_title_code)

with open(player_path, "w") as f:
    f.write(player_content)

print("Applied part 2 of bookmarks logic")
