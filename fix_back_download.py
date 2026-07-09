import re

# 1. Update DownloaderViewModel to hold activeFilter and triggerDownload
vm_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderViewModel.kt"
with open(vm_path, "r") as f:
    vm_content = f.read()

if "val activeFilter" not in vm_content:
    vm_content = vm_content.replace('val offlineUrl = mutableStateOf("")', 'val activeFilter = mutableStateOf("Search")\n    val triggerDownloadUrl = mutableStateOf<String?>(null)\n    val offlineUrl = mutableStateOf("")')
    with open(vm_path, "w") as f:
        f.write(vm_content)

# 2. Update DownloaderScreen.kt
ds_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"
with open(ds_path, "r") as f:
    ds_content = f.read()

# Add BackHandlers in DownloaderScreen
old_screens = """    if (channelUrl != null) {
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
    
    if (playingUrl != null) {
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

new_screens = """    if (channelUrl != null) {
        BackHandler { channelUrl = null }
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
    
    if (playingUrl != null) {
        BackHandler { playingUrl = null }
        PlayerScreen(
            url = playingUrl!!,
            viewModel = viewModel,
            onBack = { playingUrl = null },
            onDownload = { dlUrl ->
                playingUrl = null
                viewModel.offlineUrl.value = dlUrl
                viewModel.activeFilter.value = "Offline"
                viewModel.triggerDownloadUrl.value = dlUrl
            },
            onChannelSelected = { url ->
                channelUrl = url
            }
        )
        return
    }"""

if old_screens in ds_content:
    ds_content = ds_content.replace(old_screens, new_screens)
with open(ds_path, "w") as f:
    f.write(ds_content)

# 3. Update NewPipeTab.kt to use viewModel.activeFilter and handle triggerDownloadUrl
tab_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"
with open(tab_path, "r") as f:
    tab_content = f.read()

# Replace local selectedFilter with viewModel.activeFilter.value
old_filter = 'var selectedFilter by remember { mutableStateOf("Search") }'
if old_filter in tab_content:
    tab_content = tab_content.replace(old_filter, 'val selectedFilter = viewModel.activeFilter.value\n    val setSelectedFilter = { filter: String -> viewModel.activeFilter.value = filter }')

# Now replace `selectedFilter =` with `setSelectedFilter(`
tab_content = tab_content.replace('selectedFilter = "Search"', 'setSelectedFilter("Search")')
tab_content = tab_content.replace('selectedFilter = "History"', 'setSelectedFilter("History")')
tab_content = tab_content.replace('selectedFilter = "Offline"', 'setSelectedFilter("Offline")')
tab_content = tab_content.replace('selectedFilter = "Bookmarks"', 'setSelectedFilter("Bookmarks")')
tab_content = tab_content.replace('selectedFilter = it.title', 'setSelectedFilter(it.title)')
tab_content = tab_content.replace('selectedFilter = "Bookmark: ${it.key}"', 'setSelectedFilter("Bookmark: ${it.key}")')
tab_content = tab_content.replace('selectedFilter = "Bookmark: $name"', 'setSelectedFilter("Bookmark: $name")')

# When triggerDownloadUrl is set, we need to show the download dialog. 
# Inside the Offline block, let's catch triggerDownloadUrl
old_offline_block = """                if (currentFilter == "Offline") {
                    var qualityExpanded by remember { mutableStateOf(false) }
                    var modeExpanded by remember { mutableStateOf(false) }
                    var currentQuality by remember { mutableStateOf("720p") }
                    var currentFormat by remember { mutableStateOf("video") }"""

new_offline_block = """                if (currentFilter == "Offline") {
                    var qualityExpanded by remember { mutableStateOf(false) }
                    var modeExpanded by remember { mutableStateOf(false) }
                    var currentQuality by remember { mutableStateOf("720p") }
                    var currentFormat by remember { mutableStateOf("video") }
                    
                    LaunchedEffect(viewModel.triggerDownloadUrl.value) {
                        if (viewModel.triggerDownloadUrl.value != null) {
                            showDownloadDialog = SavedVideo(viewModel.triggerDownloadUrl.value!!, "Video", "", "", 0L)
                            viewModel.triggerDownloadUrl.value = null
                        }
                    }"""

if old_offline_block in tab_content:
    tab_content = tab_content.replace(old_offline_block, new_offline_block)

with open(tab_path, "w") as f:
    f.write(tab_content)

print("Back handlers and download routing fixed")
