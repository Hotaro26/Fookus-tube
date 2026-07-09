package com.fookus.tube.ui

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
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.activity.compose.BackHandler
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.documentfile.provider.DocumentFile
import androidx.compose.ui.res.painterResource
import com.fookus.tube.R
import com.fookus.tube.ui.theme.AppTheme
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.material.icons.filled.Check

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DownloaderScreen(viewModel: DownloaderViewModel) {
    var selectedTab by remember { mutableIntStateOf(0) }
    var playingUrl by remember { mutableStateOf<String?>(null) }
    var channelUrl by remember { mutableStateOf<String?>(null) }
    
    if (channelUrl != null) {
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
    }

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = Color.Transparent,
                tonalElevation = 0.dp
            ) {
                val rotation by animateFloatAsState(
                    targetValue = if (selectedTab == 1) 360f else 0f, 
                    animationSpec = tween(durationMillis = 500)
                )
                
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { 
                        Crossfade(targetState = selectedTab == 0, label = "home_icon") { isSelected ->
                            if (isSelected) {
                                Icon(Icons.Filled.Home, null)
                            } else {
                                Icon(Icons.Outlined.Home, null)
                            }
                        }
                    },
                    label = { Text("Home") }
                )
                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { 
                        Icon(Icons.Default.Settings, null, modifier = Modifier.rotate(rotation))
                    },
                    label = { Text("Settings") }
                )
            }
        }
    ) { innerPadding ->
        if (selectedTab == 1) {
            BackHandler {
                selectedTab = 0
            }
        }
        
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsTab(viewModel: DownloaderViewModel, contentPadding: PaddingValues = PaddingValues(0.dp)) {
    var showDiscordPopup by remember { mutableStateOf(false) }
    
    if (showDiscordPopup) {
        AlertDialog(
            onDismissRequest = { showDiscordPopup = false },
            title = { Text("Discord Details") },
            text = {
                Column {
                    Text("Discord: oi.hotaro")
                    Text("Alt ID: flawed_manago")
                }
            },
            confirmButton = {
                TextButton(onClick = { showDiscordPopup = false }) {
                    Text("Close")
                }
            }
        )
    }
    val themeMode = viewModel.themeMode.intValue
    val selectedTheme = viewModel.selectedTheme.value
    val context = LocalContext.current
    
    val folderPicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocumentTree()
    ) { uri ->
        if (uri != null) {
            context.contentResolver.takePersistableUriPermission(
                uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION
            )
            viewModel.selectedFolderUri.value = uri
            viewModel.selectedFolderName.value = DocumentFile.fromTreeUri(context, uri)?.name
        }
    }

    val clipboardManager = LocalClipboardManager.current
    val upiId = "9693703723@fam"

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(contentPadding)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Settings",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(vertical = 16.dp)
        )

        Card {
            Column(Modifier.padding(16.dp)) {
                Text("Theme Mode", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(8.dp))
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterChip(selected = themeMode == 0, onClick = { viewModel.setThemeMode(0) }, label = { Text("System") })
                    FilterChip(selected = themeMode == 1, onClick = { viewModel.setThemeMode(1) }, label = { Text("Light") })
                    FilterChip(selected = themeMode == 2, onClick = { viewModel.setThemeMode(2) }, label = { Text("Dark") })
                }
            }
        }

        Card {
            Column(Modifier.padding(16.dp)) {
                Text("App Theme", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    AppTheme.values().forEach { theme ->
                        FilterChip(
                            selected = selectedTheme == theme,
                            onClick = { viewModel.setAppTheme(theme) },
                            label = { Text(theme.name) }
                        )
                    }
                }
            }
        }


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

        Spacer(Modifier.height(24.dp))
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("About Developer", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(16.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Person, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                    Spacer(Modifier.width(16.dp))
                    Column {
                        Text("Hotaro", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                        Text("Passionate Android developer and open-source enthusiast.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                
                Spacer(Modifier.height(16.dp))
                HorizontalDivider(modifier = Modifier.alpha(0.3f))
                Spacer(Modifier.height(16.dp))
                
                Row(horizontalArrangement = Arrangement.spacedBy(24.dp, Alignment.CenterHorizontally), modifier = Modifier.fillMaxWidth()) {
                    IconButton(onClick = {
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/hotaro344"))
                        context.startActivity(intent)
                    }) {
                        Icon(painterResource(R.drawable.ic_github), contentDescription = "GitHub", tint = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    IconButton(onClick = { showDiscordPopup = true }) {
                        Icon(painterResource(R.drawable.ic_discord), contentDescription = "Discord", tint = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    IconButton(onClick = {
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://pinterest.com/hotaro344"))
                        context.startActivity(intent)
                    }) {
                        Icon(painterResource(R.drawable.ic_pinterest), contentDescription = "Pinterest", tint = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }
        
        Spacer(Modifier.height(12.dp))

        Card(
            modifier = Modifier.fillMaxWidth().clickable {
                val upiUrl = "upi://pay?pa=$upiId&pn=Donation&cu=INR"
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(upiUrl))
                try {
                    context.startActivity(intent)
                } catch (e: Exception) {
                    Toast.makeText(context, "No UPI app found", Toast.LENGTH_SHORT).show()
                }
            },
            shape = RoundedCornerShape(12.dp)
        ) {
            Row(
                Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Default.Favorite, contentDescription = null, tint = MaterialTheme.colorScheme.error)
                Spacer(Modifier.width(16.dp))
                Column {
                    Text("Support Us via UPI", fontWeight = FontWeight.Medium)
                    Text(
                        "Tap to donate",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}
