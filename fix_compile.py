import re

# 1. Update PlayerScreen.kt
player_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/PlayerScreen.kt"
with open(player_path, "r") as f:
    player_content = f.read()

sig_old = """fun PlayerScreen(
    url: String,
    onBack: () -> Unit,
    onDownload: (String) -> Unit
) {"""

sig_new = """fun PlayerScreen(
    url: String,
    viewModel: DownloaderViewModel,
    onBack: () -> Unit,
    onDownload: (String) -> Unit,
    onChannelSelected: (String) -> Unit = {}
) {"""

if sig_old in player_content:
    player_content = player_content.replace(sig_old, sig_new)

if "import androidx.compose.foundation.clickable" not in player_content:
    player_content = player_content.replace("import androidx.compose.ui.Modifier", "import androidx.compose.foundation.clickable\nimport androidx.compose.ui.Modifier")

with open(player_path, "w") as f:
    f.write(player_content)


# 2. Update ChannelScreen.kt
channel_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/ChannelScreen.kt"
with open(channel_path, "r") as f:
    channel_content = f.read()
    
if "import org.schabi.newpipe.extractor.channel.ChannelInfo" not in channel_content:
    channel_content = channel_content.replace("import org.schabi.newpipe.extractor.channel.ChannelExtractor", "import org.schabi.newpipe.extractor.channel.ChannelInfo")
    
extract_old = """                val extractor = ServiceList.YouTube.getChannelExtractor(url)
                extractor.fetchPage()
                val items = extractor.initialPage.items.filterIsInstance<StreamInfoItem>()
                withContext(Dispatchers.Main) {
                    channelName = extractor.name
                    channelAvatar = extractor.avatarUrl
                    channelBanner = extractor.bannerUrl
                    subscriberCount = extractor.subscriberCount.toString()
                    videos = items"""

extract_new = """                val channelInfo = org.schabi.newpipe.extractor.channel.ChannelInfo.getInfo(url)
                val items = channelInfo.relatedItems.filterIsInstance<StreamInfoItem>()
                withContext(Dispatchers.Main) {
                    channelName = channelInfo.name
                    channelAvatar = channelInfo.avatarUrl
                    channelBanner = channelInfo.bannerUrl
                    subscriberCount = channelInfo.subscriberCount.toString()
                    videos = items"""

if extract_old in channel_content:
    channel_content = channel_content.replace(extract_old, extract_new)

with open(channel_path, "w") as f:
    f.write(channel_content)

print("Fixed compile errors")
