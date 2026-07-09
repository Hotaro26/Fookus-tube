import os

newpipe_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"
with open(newpipe_path, "r") as f:
    np_content = f.read()

# Add imports for terminal UI and Dialog
imports_to_add = """
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.filled.Delete
import androidx.compose.ui.graphics.Color
import androidx.compose.foundation.BorderStroke
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
"""
for imp in imports_to_add.strip().split("\n"):
    if imp not in np_content:
        np_content = np_content.replace("import androidx.compose.ui.platform.LocalContext", "import androidx.compose.ui.platform.LocalContext\n" + imp)

# Replace local variables in NewPipeTab
if "var showDownloadDialog by remember" not in np_content:
    np_content = np_content.replace(
        "val history by viewModel.history",
        """val history by viewModel.history
    var showDownloadDialog by remember { mutableStateOf<SavedVideo?>(null) }
    var selectedQuality by remember { mutableStateOf("720p") }
    var isAudioOnly by remember { mutableStateOf(false) }"""
    )

# Add terminal UI inside the "Offline" section
terminal_ui = """
                    if (selectedFilter == "Offline") {
                        item {
                            val currentTerminalTheme = viewModel.terminalTheme.value
                            val consoleLogs = viewModel.consoleLogs
                            Card(
                                modifier = Modifier.fillMaxWidth().height(180.dp),
                                colors = CardDefaults.cardColors(containerColor = Color(currentTerminalTheme.background)),
                                border = BorderStroke(1.dp, Color(currentTerminalTheme.header)),
                                shape = RoundedCornerShape(16.dp)
                            ) {
                                Column(modifier = Modifier.fillMaxSize()) {
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .background(Color(currentTerminalTheme.header))
                                            .padding(horizontal = 16.dp, vertical = 8.dp),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                            Box(Modifier.size(8.dp).background(Color(0xFFFF5F56), CircleShape))
                                            Box(Modifier.size(8.dp).background(Color(0xFFFFBD2E), CircleShape))
                                            Box(Modifier.size(8.dp).background(Color(0xFF27C93F), CircleShape))
                                        }
                                        Text(
                                            text = "fookus@tube: ~",
                                            color = Color(currentTerminalTheme.text).copy(alpha = 0.6f),
                                            style = MaterialTheme.typography.labelSmall,
                                            fontFamily = FontFamily.Monospace
                                        )
                                        IconButton(
                                            onClick = { viewModel.clearConsole() },
                                            modifier = Modifier.size(16.dp)
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.Delete,
                                                contentDescription = "Clear Console",
                                                tint = Color(currentTerminalTheme.text).copy(alpha = 0.6f),
                                                modifier = Modifier.size(12.dp)
                                            )
                                        }
                                    }
                                    HorizontalDivider(color = Color(currentTerminalTheme.header), thickness = 1.dp)
                                    val lazyListState = rememberLazyListState()
                                    LaunchedEffect(consoleLogs.size) {
                                        if (consoleLogs.isNotEmpty()) {
                                            lazyListState.animateScrollToItem(consoleLogs.size - 1)
                                        }
                                    }
                                    LazyColumn(
                                        state = lazyListState,
                                        modifier = Modifier.fillMaxSize().padding(8.dp),
                                        verticalArrangement = Arrangement.spacedBy(4.dp)
                                    ) {
                                        items(consoleLogs) { log ->
                                            Text(
                                                text = log,
                                                color = Color(currentTerminalTheme.text),
                                                fontFamily = FontFamily.Monospace,
                                                fontSize = 11.sp,
                                                lineHeight = 14.sp
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
"""

if "val currentTerminalTheme = viewModel.terminalTheme.value" not in np_content:
    np_content = np_content.replace(
        "LazyColumn(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(8.dp)) {",
        "LazyColumn(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(8.dp)) {" + terminal_ui
    )

# Modify Download button to open dialog
np_content = np_content.replace(
    """viewModel.addToOffline(item)
                                            Toast.makeText(context, "Added to Offline!", Toast.LENGTH_SHORT).show()""",
    """showDownloadDialog = item"""
)

# Add Download Dialog at the bottom
download_dialog = """
    if (showDownloadDialog != null) {
        AlertDialog(
            onDismissRequest = { showDownloadDialog = null },
            title = { Text("Download Options") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Select Quality:")
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        FilterChip(selected = selectedQuality == "360p", onClick = { selectedQuality = "360p" }, label = { Text("360p") })
                        FilterChip(selected = selectedQuality == "720p", onClick = { selectedQuality = "720p" }, label = { Text("720p") })
                        FilterChip(selected = selectedQuality == "1080p", onClick = { selectedQuality = "1080p" }, label = { Text("1080p") })
                    }
                    Spacer(Modifier.height(8.dp))
                    Text("Format:")
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        FilterChip(selected = !isAudioOnly, onClick = { isAudioOnly = false }, label = { Text("Video") })
                        FilterChip(selected = isAudioOnly, onClick = { isAudioOnly = true }, label = { Text("Audio") })
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = {
                    viewModel.startMockDownload(showDownloadDialog!!, selectedQuality, if(isAudioOnly) "audio" else "video")
                    selectedFilter = "Offline"
                    showDownloadDialog = null
                }) { Text("Download") }
            },
            dismissButton = {
                TextButton(onClick = { showDownloadDialog = null }) { Text("Cancel") }
            }
        )
    }
"""
if "AlertDialog(" not in np_content:
    np_content = np_content.replace(
        "// Floating Continue Button",
        download_dialog + "\n        // Floating Continue Button"
    )

with open(newpipe_path, "w") as f:
    f.write(np_content)

# Now update DownloaderScreen.kt to add TerminalTheme settings
ds_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"
with open(ds_path, "r") as f:
    ds_content = f.read()

terminal_settings = """
        Card {
            Column(Modifier.padding(16.dp)) {
                Text("Terminal Appearance", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(8.dp))
                @OptIn(ExperimentalLayoutApi::class)
                FlowRow(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    TerminalTheme.values().forEach { theme ->
                        FilterChip(
                            selected = viewModel.terminalTheme.value == theme,
                            onClick = { viewModel.updateTerminalTheme(theme) },
                            label = { Text(theme.displayName) },
                            leadingIcon = if (viewModel.terminalTheme.value == theme) {
                                { Icon(Icons.Default.Check, null, modifier = Modifier.size(16.dp)) }
                            } else null
                        )
                    }
                }
            }
        }
"""
if "TerminalTheme.values()" not in ds_content:
    ds_content = ds_content.replace("import androidx.compose.foundation.verticalScroll", "import androidx.compose.foundation.verticalScroll\nimport androidx.compose.foundation.layout.FlowRow\nimport androidx.compose.foundation.layout.ExperimentalLayoutApi\nimport androidx.compose.material.icons.filled.Check")
    
    # insert before "Download Location" card
    ds_content = ds_content.replace(
        """        Card(
            modifier = Modifier.fillMaxWidth().clickable { folderPicker.launch(null) }""",
        terminal_settings + "\n" + """        Card(
            modifier = Modifier.fillMaxWidth().clickable { folderPicker.launch(null) }"""
    )
    
with open(ds_path, "w") as f:
    f.write(ds_content)

print("UI components patched.")
