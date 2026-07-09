import re

# 1. Update DownloaderScreen.kt
ds_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"
with open(ds_path, "r") as f:
    ds_content = f.read()

channel_state = """    var selectedTab by remember { mutableIntStateOf(0) }
    var playingUrl by remember { mutableStateOf<String?>(null) }
    var channelUrl by remember { mutableStateOf<String?>(null) }
    
    if (channelUrl != null) {
        ChannelScreen(
            url = channelUrl!!,
            onBack = { channelUrl = null },
            onVideoSelected = { url ->
                playingUrl = url
                channelUrl = null
            }
        )
        return
    }
"""
if "var channelUrl" not in ds_content:
    ds_content = ds_content.replace("""    var selectedTab by remember { mutableIntStateOf(0) }
    var playingUrl by remember { mutableStateOf<String?>(null) }""", channel_state)
    
    # Add onChannelSelected to PlayerScreen
    ds_content = ds_content.replace(
        """onDownload = { dlUrl ->
                playingUrl = null
                // We don't download in FookusTube
            }
        )""",
        """onDownload = { dlUrl ->
                playingUrl = null
            },
            onChannelSelected = { url ->
                channelUrl = url
            }
        )"""
    )
    with open(ds_path, "w") as f:
        f.write(ds_content)

# 2. Update PlayerScreen.kt
player_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/PlayerScreen.kt"
with open(player_path, "r") as f:
    player_content = f.read()

if "onChannelSelected: (String) -> Unit" not in player_content:
    player_content = player_content.replace(
        "fun PlayerScreen(url: String, viewModel: DownloaderViewModel, onBack: () -> Unit, onDownload: (String) -> Unit) {",
        "fun PlayerScreen(url: String, viewModel: DownloaderViewModel, onBack: () -> Unit, onDownload: (String) -> Unit, onChannelSelected: (String) -> Unit = {}) {"
    )
    
    # Add clickable to the Channel Info row
    channel_row_old = """                            Row(verticalAlignment = Alignment.CenterVertically) {
                                // Channel Info
                                val avatarUrl = ext.uploaderAvatars?.firstOrNull()?.url"""
    
    channel_row_new = """                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.clickable { ext.uploaderUrl?.let { onChannelSelected(it) } }.padding(8.dp)
                            ) {
                                // Channel Info
                                val avatarUrl = ext.uploaderAvatars?.firstOrNull()?.url"""
    
    player_content = player_content.replace(channel_row_old, channel_row_new)
    
    with open(player_path, "w") as f:
        f.write(player_content)

print("Wired up ChannelScreen")
