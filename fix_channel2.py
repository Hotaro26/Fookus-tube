import re

channel_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/ChannelScreen.kt"
with open(channel_path, "r") as f:
    content = f.read()

# Replace the try/catch block with a simple implementation
old_effect = """    LaunchedEffect(url) {
        scope.launch(Dispatchers.IO) {
            try {
                val channelInfo = ChannelInfo.getInfo(url)
                val tabs = channelInfo.tabs
                val tabInfo = org.schabi.newpipe.extractor.channel.tabs.ChannelTabInfo.getInfo(ServiceList.YouTube, tabs.firstOrNull { it.content?.contains("Video") == true } ?: tabs.first())
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
    }"""

new_effect = """    LaunchedEffect(url) {
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
    }"""

if old_effect in content:
    content = content.replace(old_effect, new_effect)
else:
    # Just regex replace
    content = re.sub(r'LaunchedEffect\(url\) \{.*?^\s+Scaffold\(', new_effect + '\n    \n    Scaffold(', content, flags=re.DOTALL | re.MULTILINE)

with open(channel_path, "w") as f:
    f.write(content)

print("Fixed channel screen extraction again")
