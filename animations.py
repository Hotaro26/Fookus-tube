import re

# 1. Remove Download Location from Settings
ds_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"
with open(ds_path, "r") as f:
    ds_content = f.read()

download_location_card = """        Card(
            modifier = Modifier.fillMaxWidth().clickable { folderPicker.launch(null) },
            shape = RoundedCornerShape(12.dp)
        ) {
            Row(
                Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Default.Folder, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.width(16.dp))
                Column {
                    Text("Download Location", fontWeight = FontWeight.Medium)
                    Text(
                        viewModel.selectedFolderName.value ?: "Not selected",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }"""

if download_location_card in ds_content:
    ds_content = ds_content.replace(download_location_card, "")
    with open(ds_path, "w") as f:
        f.write(ds_content)


# 2 & 3. NewPipeTab bouncy effects
np_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"
with open(np_path, "r") as f:
    np_content = f.read()

# Make sure imports are present
imports_to_add = """
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.Spring
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.ui.draw.scale
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.interaction.collectIsHoveredAsState
"""

if "import androidx.compose.animation.core.spring" not in np_content:
    np_content = np_content.replace("import androidx.compose.ui.Modifier", "import androidx.compose.ui.Modifier" + imports_to_add)

# Replace History and Offline pills with bouncy scaled versions
pills_old = """            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "History" },
                    label = { Text("History") }
                )
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "Offline" },
                    label = { Text("Offline") }
                )
            }"""

pills_new = """            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                val historyInteraction = remember { MutableInteractionSource() }
                val historyPressed by historyInteraction.collectIsPressedAsState()
                val historyScale by animateFloatAsState(if (historyPressed) 0.8f else 1.0f, animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy))
                
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "History" },
                    label = { Text("History") },
                    modifier = Modifier.scale(historyScale),
                    interactionSource = historyInteraction
                )
                
                val offlineInteraction = remember { MutableInteractionSource() }
                val offlinePressed by offlineInteraction.collectIsPressedAsState()
                val offlineScale by animateFloatAsState(if (offlinePressed) 0.8f else 1.0f, animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy))
                
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "Offline" },
                    label = { Text("Offline") },
                    modifier = Modifier.scale(offlineScale),
                    interactionSource = offlineInteraction
                )
            }"""

if pills_old in np_content:
    np_content = np_content.replace(pills_old, pills_new)

# 3. Replace continue FAB with circular effect
fab_old = """        val lastPlayed = viewModel.lastPlayedUrl.value
        if (lastPlayed != null) {
            ExtendedFloatingActionButton(
                onClick = { onUrlSelected(lastPlayed) },
                modifier = Modifier.align(Alignment.BottomEnd).padding(end = 16.dp, bottom = 16.dp + contentPadding.calculateBottomPadding()),
                containerColor = MaterialTheme.colorScheme.primary,
                icon = { Icon(Icons.Default.PlayArrow, contentDescription = "Continue playing") },
                text = { Text("Continue") },
                shape = RoundedCornerShape(12.dp)
            )
        }"""

fab_new = """        val lastPlayed = viewModel.lastPlayedUrl.value
        if (lastPlayed != null) {
            val fabInteraction = remember { MutableInteractionSource() }
            val fabPressed by fabInteraction.collectIsPressedAsState()
            val fabHovered by fabInteraction.collectIsHoveredAsState()
            val isFabActive = fabPressed || fabHovered
            val animatedRadius by animateDpAsState(targetValue = if (isFabActive) 50.dp else 12.dp, animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy))

            ExtendedFloatingActionButton(
                onClick = { onUrlSelected(lastPlayed) },
                modifier = Modifier.align(Alignment.BottomEnd).padding(end = 16.dp, bottom = 16.dp + contentPadding.calculateBottomPadding()),
                containerColor = MaterialTheme.colorScheme.primary,
                icon = { Icon(Icons.Default.PlayArrow, contentDescription = "Continue playing") },
                text = { Text("Continue") },
                shape = RoundedCornerShape(animatedRadius),
                interactionSource = fabInteraction
            )
        }"""

if fab_old in np_content:
    np_content = np_content.replace(fab_old, fab_new)

with open(np_path, "w") as f:
    f.write(np_content)
    
print("Applied all animation and setting updates")
