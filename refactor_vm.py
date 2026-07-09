import os

file_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderViewModel.kt"

new_content = """package com.fookus.tube.ui

import android.app.Application
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import com.fookus.tube.ui.theme.AppTheme
import org.schabi.newpipe.extractor.stream.StreamInfoItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class DownloaderViewModel(application: Application) : AndroidViewModel(application) {

    // App Preferences
    val themeMode = mutableIntStateOf(0) // 0: System, 1: Light, 2: Dark
    val selectedTheme = mutableStateOf(AppTheme.PURPLE)

    fun setThemeMode(mode: Int) {
        themeMode.intValue = mode
    }

    fun setAppTheme(theme: AppTheme) {
        selectedTheme.value = theme
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
    var newPipeQuery = mutableStateOf("")
    var newPipeResults = mutableStateOf<List<StreamInfoItem>>(emptyList())
}
"""

with open(file_path, "w") as f:
    f.write(new_content)

print("DownloaderViewModel.kt rewritten.")
