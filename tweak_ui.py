import os
import re

newpipe_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"

with open(newpipe_path, "r") as f:
    content = f.read()

# 1. Compute listToShow before Column
list_to_show_calc = """    val listToShow = when (selectedFilter) {
        "History" -> history
        "Offline" -> offline
        else -> results.map { 
            SavedVideo(it.url, it.name, it.uploaderName, it.thumbnails?.firstOrNull()?.url ?: "")
        }
    }
    val isListEmpty = listToShow.isEmpty() && !isLoading
"""

column_start = """        Column(
            modifier = Modifier.fillMaxSize().padding(contentPadding).padding(horizontal = 16.dp),
            verticalArrangement = if (isListEmpty) Arrangement.Center else Arrangement.Top,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {"""

# Replace old Column
old_column = """        Column(
            modifier = Modifier.fillMaxSize().padding(contentPadding).padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.Top,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {"""

if old_column in content:
    content = content.replace(old_column, list_to_show_calc + "\n" + column_start)

# 2. Remove the inner calculation of listToShow
inner_list = """                val listToShow = when (selectedFilter) {
                    "History" -> history
                    "Offline" -> offline
                    else -> results.map { 
                        SavedVideo(it.url, it.name, it.uploaderName, it.thumbnails?.firstOrNull()?.url ?: "")
                    }
                }
                
                if (listToShow.isEmpty()) {"""

if inner_list in content:
    content = content.replace(inner_list, "                if (listToShow.isEmpty()) {")

# 3. Change FloatingActionButton shape
fab_old = """            FloatingActionButton(
                onClick = { onUrlSelected(lastPlayed) },
                modifier = Modifier.align(Alignment.BottomEnd).padding(end = 16.dp, bottom = 16.dp + contentPadding.calculateBottomPadding()),
                containerColor = MaterialTheme.colorScheme.primary
            ) {"""

fab_new = """            ExtendedFloatingActionButton(
                onClick = { onUrlSelected(lastPlayed) },
                modifier = Modifier.align(Alignment.BottomEnd).padding(end = 16.dp, bottom = 16.dp + contentPadding.calculateBottomPadding()),
                containerColor = MaterialTheme.colorScheme.primary,
                icon = { Icon(Icons.Default.PlayArrow, contentDescription = "Continue playing") },
                text = { Text("Continue") },
                shape = RoundedCornerShape(12.dp)
            )"""

if fab_old in content:
    # also remove the old icon
    icon_line = '                Icon(Icons.Default.PlayArrow, contentDescription = "Continue playing")\n            }'
    # We will just replace it using regex
    content = re.sub(
        r'FloatingActionButton\([\s\S]*?Icon\(Icons\.Default\.PlayArrow, contentDescription = "Continue playing"\)\s*\}',
        fab_new,
        content
    )


with open(newpipe_path, "w") as f:
    f.write(content)

print("Applied tweaks")
