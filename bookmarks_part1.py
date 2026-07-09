import re

# 1. Update DownloaderViewModel.kt for bookmarks
vm_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderViewModel.kt"
with open(vm_path, "r") as f:
    vm_content = f.read()

bookmarks_state = """    val offline = mutableStateOf<List<SavedVideo>>(emptyList())
    val bookmarks = mutableStateOf<Map<String, List<SavedVideo>>>(mapOf("Watch Later" to emptyList()))"""

if "val bookmarks =" not in vm_content:
    vm_content = vm_content.replace("    val offline = mutableStateOf<List<SavedVideo>>(emptyList())", bookmarks_state)

load_bookmarks = """        val savedOffline = prefs.getString("offline_list", "[]")
        offline.value = try { Json.decodeFromString(savedOffline!!) } catch (e: Exception) { emptyList() }
        
        val savedBookmarks = prefs.getString("bookmarks_list", "{\\"Watch Later\\":[]}")
        bookmarks.value = try { Json.decodeFromString(savedBookmarks!!) } catch (e: Exception) { mapOf("Watch Later" to emptyList()) }"""

if "savedBookmarks =" not in vm_content:
    vm_content = vm_content.replace("""        val savedOffline = prefs.getString("offline_list", "[]")
        offline.value = try { Json.decodeFromString(savedOffline!!) } catch (e: Exception) { emptyList() }""", load_bookmarks)

save_bookmarks_func = """    fun addBookmarkPlaylist(name: String) {
        if (!bookmarks.value.containsKey(name)) {
            val newMap = bookmarks.value.toMutableMap()
            newMap[name] = emptyList()
            bookmarks.value = newMap
            saveBookmarks()
        }
    }

    fun addVideoToBookmark(playlist: String, video: SavedVideo) {
        val newMap = bookmarks.value.toMutableMap()
        val currentList = newMap[playlist]?.toMutableList() ?: mutableListOf()
        if (currentList.none { it.url == video.url }) {
            currentList.add(0, video)
            newMap[playlist] = currentList
            bookmarks.value = newMap
            saveBookmarks()
        }
    }

    private fun saveBookmarks() {
        prefs.edit().putString("bookmarks_list", Json.encodeToString(bookmarks.value)).apply()
    }
"""

if "fun addBookmarkPlaylist" not in vm_content:
    vm_content = vm_content.replace("    fun addToHistory(video: SavedVideo) {", save_bookmarks_func + "\n    fun addToHistory(video: SavedVideo) {")

with open(vm_path, "w") as f:
    f.write(vm_content)


# 2. Update NewPipeTab.kt to show Bookmarks pill and handle it
np_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"
with open(np_path, "r") as f:
    np_content = f.read()

if "FilterChip(selected = false, onClick = { selectedFilter = \"Bookmarks\" }, label = { Text(\"Bookmarks\") })" not in np_content:
    old_pills = """                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "Offline" },
                    label = { Text("Offline") }
                )"""
    new_pills = """                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "Offline" },
                    label = { Text("Offline") }
                )
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "Bookmarks" },
                    label = { Text("Bookmarks") }
                )"""
    np_content = np_content.replace(old_pills, new_pills)

# Handle back handler for bookmarks
if 'currentFilter.startsWith("Bookmark:")' not in np_content:
    np_content = np_content.replace("""if (currentFilter != "Search") {
            BackHandler {
                selectedFilter = "Search"
            }""", """if (currentFilter != "Search") {
            BackHandler {
                if (currentFilter.startsWith("Bookmark:")) {
                    selectedFilter = "Bookmarks"
                } else {
                    selectedFilter = "Search"
                }
            }""")

# Handle rendering Bookmarks
render_list_old = """val listToShow = if (currentFilter == "History") history else offline"""
render_list_new = """val listToShow = when {
                    currentFilter == "History" -> history
                    currentFilter == "Offline" -> offline
                    currentFilter.startsWith("Bookmark:") -> {
                        val playlistName = currentFilter.removePrefix("Bookmark: ")
                        viewModel.bookmarks.value[playlistName] ?: emptyList()
                    }
                    else -> emptyList()
                }"""
if render_list_old in np_content:
    np_content = np_content.replace(render_list_old, render_list_new)

# Add Bookmarks rendering logic when currentFilter == "Bookmarks"
if 'if (currentFilter == "Offline") {' in np_content and 'if (currentFilter == "Bookmarks")' not in np_content:
    offline_block = """                if (currentFilter == "Offline") {"""
    bookmarks_block = """                if (currentFilter == "Bookmarks") {
                    LazyColumn(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(viewModel.bookmarks.value.keys.toList()) { playlistName ->
                            Card(
                                modifier = Modifier.fillMaxWidth().clickable { selectedFilter = "Bookmark: $playlistName" },
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
                
                if (currentFilter == "Offline") {"""
    np_content = np_content.replace(offline_block, bookmarks_block)
    
    # Need to add import for Bookmarks icon
    np_content = np_content.replace("import androidx.compose.material.icons.filled.ArrowBack", "import androidx.compose.material.icons.filled.ArrowBack\nimport androidx.compose.material.icons.filled.Bookmarks")

with open(np_path, "w") as f:
    f.write(np_content)


# 3. Update PlayerScreen.kt to show bookmark star icon and dialog
player_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/PlayerScreen.kt"
with open(player_path, "r") as f:
    player_content = f.read()

# Add dialog state and icon
if "var showBookmarkDialog by remember { mutableStateOf(false) }" not in player_content:
    # First add imports
    imports = """import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Add
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.TextButton
import androidx.compose.material3.OutlinedTextField
import com.fookus.tube.model.SavedVideo
"""
    player_content = player_content.replace("import androidx.compose.ui.Modifier", imports + "\nimport androidx.compose.ui.Modifier")

    # In PlayerScreen definition: we need viewModel to access bookmarks. But PlayerScreen doesn't take viewModel right now.
    # We will pass viewModel to PlayerScreen.
    pass

with open(player_path, "w") as f:
    f.write(player_content)
