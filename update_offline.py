import os

vm_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderViewModel.kt"
with open(vm_path, "r") as f:
    vm_content = f.read()

if "val offlineUrl =" not in vm_content:
    vm_content = vm_content.replace(
        "val history = mutableStateOf<List<SavedVideo>>(emptyList())",
        "val offlineUrl = mutableStateOf(\"\")\n    val history = mutableStateOf<List<SavedVideo>>(emptyList())"
    )

with open(vm_path, "w") as f:
    f.write(vm_content)

newpipe_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"
with open(newpipe_path, "r") as f:
    np_content = f.read()

# I will replace the offline section in NewPipeTab.
# Currently, it shows the Terminal then the LazyColumn of offline videos.
# I need to insert the Offline Input UI before the terminal.

offline_ui = """
                if (selectedFilter == "Offline") {
                    var qualityExpanded by remember { mutableStateOf(false) }
                    var modeExpanded by remember { mutableStateOf(false) }
                    var currentQuality by remember { mutableStateOf("720p") }
                    var currentFormat by remember { mutableStateOf("video") }
                    
                    OutlinedTextField(
                        value = viewModel.offlineUrl.value,
                        onValueChange = { viewModel.offlineUrl.value = it },
                        placeholder = { Text("Paste YouTube URL here") },
                        modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
                        trailingIcon = {
                            Row {
                                if (viewModel.offlineUrl.value.isNotEmpty()) {
                                    IconButton(onClick = { viewModel.offlineUrl.value = "" }) {
                                        Icon(Icons.Default.Close, contentDescription = "Clear")
                                    }
                                }
                                IconButton(onClick = { 
                                    androidx.compose.ui.platform.LocalClipboardManager.current.getText()?.let { 
                                        viewModel.offlineUrl.value = it.text
                                    }
                                }) {
                                    Icon(androidx.compose.material.icons.Icons.Default.ContentPaste, "Paste")
                                }
                            }
                        },
                        shape = MaterialTheme.shapes.large
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        ExposedDropdownMenuBox(
                            expanded = qualityExpanded,
                            onExpandedChange = { qualityExpanded = it },
                            modifier = Modifier.weight(1f)
                        ) {
                            OutlinedTextField(
                                value = currentQuality,
                                onValueChange = {},
                                readOnly = true,
                                label = { Text("Quality") },
                                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = qualityExpanded) },
                                modifier = Modifier.menuAnchor(),
                                shape = RoundedCornerShape(12.dp)
                            )
                            ExposedDropdownMenu(
                                expanded = qualityExpanded,
                                onDismissRequest = { qualityExpanded = false }
                            ) {
                                listOf("360p", "720p", "1080p").forEach { selectionOption ->
                                    DropdownMenuItem(
                                        text = { Text(selectionOption) },
                                        onClick = {
                                            currentQuality = selectionOption
                                            qualityExpanded = false
                                        }
                                    )
                                }
                            }
                        }
                        
                        ExposedDropdownMenuBox(
                            expanded = modeExpanded,
                            onExpandedChange = { modeExpanded = it },
                            modifier = Modifier.weight(1f)
                        ) {
                            OutlinedTextField(
                                value = currentFormat,
                                onValueChange = {},
                                readOnly = true,
                                label = { Text("Format") },
                                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = modeExpanded) },
                                modifier = Modifier.menuAnchor(),
                                shape = RoundedCornerShape(12.dp)
                            )
                            ExposedDropdownMenu(
                                expanded = modeExpanded,
                                onDismissRequest = { modeExpanded = false }
                            ) {
                                listOf("video", "audio").forEach { selectionOption ->
                                    DropdownMenuItem(
                                        text = { Text(selectionOption) },
                                        onClick = {
                                            currentFormat = selectionOption
                                            modeExpanded = false
                                        }
                                    )
                                }
                            }
                        }
                    }

                    Button(
                        onClick = {
                            if (viewModel.offlineUrl.value.isNotBlank()) {
                                val savedItem = SavedVideo(viewModel.offlineUrl.value, "Manual Download", "Unknown", "")
                                viewModel.startMockDownload(savedItem, currentQuality, currentFormat, context)
                            }
                        },
                        modifier = Modifier.fillMaxWidth().height(56.dp).padding(bottom = 16.dp),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Icon(Icons.Default.Download, null)
                        Spacer(Modifier.width(8.dp))
                        Text("Download")
                    }
                    
                    val currentTerminalTheme = viewModel.terminalTheme.value
"""

if "var currentQuality by remember" not in np_content:
    # We replace:
    #                 if (selectedFilter == "Offline") {
    #                     val currentTerminalTheme = viewModel.terminalTheme.value
    
    np_content = np_content.replace(
        """                if (selectedFilter == "Offline") {
                    val currentTerminalTheme = viewModel.terminalTheme.value""",
        offline_ui
    )

if "import androidx.compose.material.icons.filled.ContentPaste" not in np_content:
    np_content = np_content.replace("import androidx.compose.material.icons.filled.Close", "import androidx.compose.material.icons.filled.Close\nimport androidx.compose.material.icons.filled.ContentPaste")

# Change the download dialog behavior
# When downloading from search results:
download_dialog_confirm = """                confirmButton = {
                    TextButton(onClick = {
                        viewModel.offlineUrl.value = showDownloadDialog!!.url
                        viewModel.startMockDownload(showDownloadDialog!!, selectedQuality, if(isAudioOnly) "audio" else "video", context)
                        selectedFilter = "Offline"
                        showDownloadDialog = null
                    }) { Text("Download") }
                },"""

old_download_dialog_confirm = """                confirmButton = {
                    TextButton(onClick = {
                        viewModel.startMockDownload(showDownloadDialog!!, selectedQuality, if(isAudioOnly) "audio" else "video", context)
                        selectedFilter = "Offline"
                        showDownloadDialog = null
                    }) { Text("Download") }
                },"""

if old_download_dialog_confirm in np_content:
    np_content = np_content.replace(old_download_dialog_confirm, download_dialog_confirm)

with open(newpipe_path, "w") as f:
    f.write(np_content)
    
print("Updated offline UI")
