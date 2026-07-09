import re

channel_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/ChannelScreen.kt"
with open(channel_path, "r") as f:
    content = f.read()

new_logic = """                val channelInfo = ChannelInfo.getInfo(url)
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
                }"""

old_logic = """                val channelInfo = ChannelInfo.getInfo(url)
                val items = channelInfo.relatedItems.filterIsInstance<StreamInfoItem>()
                withContext(Dispatchers.Main) {
                    channelName = channelInfo.name
                    videos = items
                    isLoading = false
                }"""

old_logic_2 = """                val channelInfo = ChannelInfo.getInfo(url)
                val items = channelInfo.relatedItems
                withContext(Dispatchers.Main) {
                    channelName = channelInfo.name
                    videos = items.filterIsInstance<StreamInfoItem>()
                    isLoading = false
                }"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)
elif old_logic_2 in content:
    content = content.replace(old_logic_2, new_logic)
elif "try {\n                val channelInfo" in content:
    content = re.sub(r'val channelInfo = ChannelInfo\.getInfo\(url\).*?isLoading = false\n                }', new_logic, content, flags=re.DOTALL)

# Add missing state variables if they are not there
if "var channelAvatar by remember" not in content:
    content = content.replace('var channelName by remember { mutableStateOf("") }', 'var channelName by remember { mutableStateOf("") }\n    var channelAvatar by remember { mutableStateOf<String?>(null) }\n    var channelBanner by remember { mutableStateOf<String?>(null) }\n    var subscriberCount by remember { mutableStateOf("") }')
    
# Add banner rendering in LazyColumn if it's not there
if "if (channelBanner != null)" not in content:
    item_header = """                item {
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
                
                items(videos) {"""
    content = content.replace("items(videos) {", item_header)

with open(channel_path, "w") as f:
    f.write(content)

print("Fixed channel screen extraction logic")
