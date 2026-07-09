import os
import re

gabi_vm_path = "/home/hotaro/Projects/gabi/app/src/androidMain/kotlin/com/material/downloader/ui/DownloaderViewModel.kt"
fookus_vm_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderViewModel.kt"

# First, rewrite DownloaderViewModel for FookusTube to include settings variables
fookus_vm_code = """package com.fookus.tube.ui

import android.app.Application
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import com.fookus.tube.ui.theme.AppTheme
import org.schabi.newpipe.extractor.stream.StreamInfoItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import android.net.Uri

class DownloaderViewModel(application: Application) : AndroidViewModel(application) {

    // App Preferences
    val themeMode = mutableIntStateOf(0) // 0: System, 1: Light, 2: Dark
    val selectedTheme = mutableStateOf(AppTheme.Default)
    val selectedFolderUri = mutableStateOf<Uri?>(null)
    val selectedFolderName = mutableStateOf<String?>(null)
    val terminalTheme = mutableStateOf(0)

    fun setThemeMode(mode: Int) {
        themeMode.intValue = mode
    }

    fun setAppTheme(theme: AppTheme) {
        selectedTheme.value = theme
    }

    fun updateTerminalTheme(theme: Int) {
        terminalTheme.value = theme
    }

    // Shared intents
    private val _externalUrl = MutableStateFlow<String?>(null)
    val externalUrl: StateFlow<String?> = _externalUrl
    
    fun handleSharedUrl(url: String) {
        _externalUrl.value = url
    }

    fun consumeSharedUrl() {
        _externalUrl.value = null
    }

    // NewPipe Search State
    val newPipeQuery = mutableStateOf("")
    val newPipeResults = mutableStateOf<List<StreamInfoItem>>(emptyList())
}
"""

with open(fookus_vm_path, "w") as f:
    f.write(fookus_vm_code)


gabi_screen_path = "/home/hotaro/Projects/gabi/app/src/androidMain/kotlin/com/material/downloader/ui/DownloaderScreen.kt"
fookus_screen_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"

# Extract SettingsTab from Gabi
with open(gabi_screen_path, "r") as f:
    gabi_screen_content = f.read()

settings_idx = gabi_screen_content.find("@Composable\nfun SettingsTab")
logs_tab_idx = gabi_screen_content.find("@Composable\nfun LogsTab")
if settings_idx != -1 and logs_tab_idx != -1:
    settings_code = gabi_screen_content[settings_idx:logs_tab_idx]
    # Replace package references
    settings_code = settings_code.replace("com.material.downloader", "com.fookus.tube")
else:
    settings_code = ""

# Rewrite FookusTube DownloaderScreen
fookus_screen_code = """package com.fookus.tube.ui

import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.documentfile.provider.DocumentFile
import com.fookus.tube.ui.theme.AppTheme
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.ui.platform.LocalClipboardManager

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DownloaderScreen(viewModel: DownloaderViewModel) {
    var selectedTab by remember { mutableIntStateOf(0) }
    var playingUrl by remember { mutableStateOf<String?>(null) }
    
    if (playingUrl != null) {
        PlayerScreen(
            url = playingUrl!!,
            onBack = { playingUrl = null },
            onDownload = { dlUrl ->
                playingUrl = null
                // We don't download in FookusTube
            }
        )
        return
    }

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = Color.Transparent,
                tonalElevation = 0.dp
            ) {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { Icon(Icons.Default.PlayArrow, null) },
                    label = { Text("Home") }
                )
                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { Icon(Icons.Default.Settings, null) },
                    label = { Text("Settings") }
                )
            }
        }
    ) { innerPadding ->
        AnimatedContent(targetState = selectedTab, label = "tab_transition") { targetTab ->
            when (targetTab) {
                0 -> NewPipeTab(
                    viewModel = viewModel,
                    contentPadding = innerPadding,
                    onUrlSelected = { url -> playingUrl = url }
                )
                1 -> SettingsTab(viewModel, innerPadding)
            }
        }
    }
}

""" + settings_code

with open(fookus_screen_path, "w") as f:
    f.write(fookus_screen_code)

print("Files patched successfully!")
