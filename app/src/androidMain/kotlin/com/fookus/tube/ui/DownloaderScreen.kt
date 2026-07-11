package com.fookus.tube.ui

import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.clickable
import androidx.compose.foundation.background
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
import androidx.compose.ui.platform.LocalConfiguration
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

    val configuration = LocalConfiguration.current
    val isTablet = configuration.screenWidthDp >= 600

    val navigationContent: @Composable () -> Unit = {
        val rotation by animateFloatAsState(
            targetValue = if (selectedTab == 1) 360f else 0f, 
            animationSpec = tween(durationMillis = 500)
        )
        
        if (isTablet) {
            NavigationRail(
                containerColor = Color.Transparent
            ) {
                Spacer(Modifier.weight(1f))
                NavigationRailItem(
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
                NavigationRailItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { 
                        Icon(Icons.Default.Settings, null, modifier = Modifier.rotate(rotation))
                    },
                    label = { Text("Settings") }
                )
                Spacer(Modifier.weight(1f))
            }
        } else {
            NavigationBar(
                containerColor = Color.Transparent,
                tonalElevation = 0.dp
            ) {
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
    }

    Row(modifier = Modifier.fillMaxSize()) {
        if (isTablet) {
            navigationContent()
        }
        
        Scaffold(
            modifier = Modifier.weight(1f),
            bottomBar = {
                if (!isTablet) {
                    navigationContent()
                }
            }
        ) { innerPadding ->
            if (selectedTab == 1) {
                BackHandler {
                    selectedTab = 0
                }
            }
            
            val screenMargin = if (isTablet) (configuration.screenWidthDp * 0.20f).dp else 0.dp
            
            Box(modifier = Modifier.fillMaxSize().padding(horizontal = screenMargin)) {
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
    }
}

@OptIn(ExperimentalMaterial3Api::class, androidx.compose.animation.ExperimentalAnimationApi::class)
@Composable
fun SettingsTab(viewModel: DownloaderViewModel, contentPadding: PaddingValues = PaddingValues(0.dp)) {
    var currentScreen by remember { mutableStateOf("Main") }

    BackHandler(enabled = currentScreen != "Main") {
        currentScreen = "Main"
    }

    AnimatedContent(
        targetState = currentScreen,
        transitionSpec = {
            if (targetState != "Main") {
                slideIntoContainer(
                    towards = AnimatedContentTransitionScope.SlideDirection.Left,
                    animationSpec = tween(300)
                ) togetherWith slideOutOfContainer(
                    towards = AnimatedContentTransitionScope.SlideDirection.Left,
                    animationSpec = tween(300)
                )
            } else {
                slideIntoContainer(
                    towards = AnimatedContentTransitionScope.SlideDirection.Right,
                    animationSpec = tween(300)
                ) togetherWith slideOutOfContainer(
                    towards = AnimatedContentTransitionScope.SlideDirection.Right,
                    animationSpec = tween(300)
                )
            }
        },
        label = "settings_transition"
    ) { screen ->
        when (screen) {
            "Main" -> SettingsMainList(onNavigate = { currentScreen = it }, contentPadding = contentPadding)
            "Customisation" -> CustomisationScreen(viewModel, onBack = { currentScreen = "Main" }, contentPadding = contentPadding)
            "Sources" -> SourcesScreen(viewModel, onBack = { currentScreen = "Main" }, contentPadding = contentPadding)
            "About" -> AboutScreen(onBack = { currentScreen = "Main" }, contentPadding = contentPadding)
            "Story" -> StoryScreen(onBack = { currentScreen = "Main" }, contentPadding = contentPadding)
        }
    }
}

@Composable
fun SettingsListItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    iconColor: androidx.compose.ui.graphics.Color,
    title: String,
    subtitle: String,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
            .padding(horizontal = 20.dp, vertical = 16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(48.dp)
                .background(iconColor, shape = androidx.compose.foundation.shape.CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Icon(icon, contentDescription = null, tint = androidx.compose.ui.graphics.Color.White)
        }
        Spacer(Modifier.width(20.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Text(
                subtitle,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 1,
                overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
fun SettingsMainList(onNavigate: (String) -> Unit, contentPadding: PaddingValues) {
    val context = androidx.compose.ui.platform.LocalContext.current
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
        
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
        ) {
            Column {
                SettingsListItem(
                    icon = Icons.Default.Palette,
                    iconColor = androidx.compose.ui.graphics.Color(0xFF88637B),
                    title = "Customisation",
                    subtitle = "Themes, App Appearance, Terminal",
                    onClick = { onNavigate("Customisation") }
                )
                HorizontalDivider(modifier = Modifier.alpha(0.1f))
                SettingsListItem(
                    icon = Icons.Default.Search,
                    iconColor = androidx.compose.ui.graphics.Color(0xFF00758F),
                    title = "Sources",
                    subtitle = "Search engines like YouTube, PeerTube",
                    onClick = { onNavigate("Sources") }
                )
                HorizontalDivider(modifier = Modifier.alpha(0.1f))
                SettingsListItem(
                    icon = Icons.Default.Info,
                    iconColor = androidx.compose.ui.graphics.Color(0xFF4C6B8B),
                    title = "About",
                    subtitle = "Developer info, GitHub, Support",
                    onClick = { onNavigate("About") }
                )
                HorizontalDivider(modifier = Modifier.alpha(0.1f))
                SettingsListItem(
                    icon = Icons.Default.Book,
                    iconColor = androidx.compose.ui.graphics.Color(0xFF7A4F5C),
                    title = "Story",
                    subtitle = "The journey of this app",
                    onClick = { onNavigate("Story") }
                )
                HorizontalDivider(modifier = Modifier.alpha(0.1f))
                val context = LocalContext.current
                val packageInfo = remember {
                    try {
                        context.packageManager.getPackageInfo(context.packageName, 0)
                    } catch (e: Exception) {
                        null
                    }
                }
                val versionName = packageInfo?.versionName ?: "Unknown"

                SettingsListItem(
                    icon = Icons.Default.Info,
                    iconColor = androidx.compose.ui.graphics.Color(0xFF6B8B4C),
                    title = "App Info",
                    subtitle = "Version $versionName",
                    onClick = {
                        val intent = android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("https://github.com/Hotaro26/fookus-tube"))
                        context.startActivity(intent)
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun CustomisationScreen(viewModel: DownloaderViewModel, onBack: () -> Unit, contentPadding: PaddingValues) {
    val themeMode = viewModel.themeMode.intValue
    val selectedTheme = viewModel.selectedTheme.value
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(contentPadding)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 16.dp)) {
            IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, "Back") }
            Spacer(Modifier.width(8.dp))
            Text("Customisation", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        }
        
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
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SourcesScreen(viewModel: DownloaderViewModel, onBack: () -> Unit, contentPadding: PaddingValues) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(contentPadding)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 16.dp)) {
            IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, "Back") }
            Spacer(Modifier.width(8.dp))
            Text("Sources", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        }
        
        Card {
            Column(Modifier.padding(16.dp)) {
                Text("Search Engine", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(8.dp))
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterChip(selected = viewModel.searchSource.value == "YouTube", onClick = { viewModel.searchSource.value = "YouTube" }, label = { Text("YouTube") })
                    FilterChip(selected = viewModel.searchSource.value == "PeerTube", onClick = { viewModel.searchSource.value = "PeerTube" }, label = { Text("PeerTube") })
                    FilterChip(selected = viewModel.searchSource.value == "SoundCloud", onClick = { viewModel.searchSource.value = "SoundCloud" }, label = { Text("SoundCloud") })
                }
            }
        }
    }
}

@Composable
fun AboutScreen(onBack: () -> Unit, contentPadding: PaddingValues) {
    val context = LocalContext.current
    var showDiscordPopup by remember { mutableStateOf(false) }
    val upiId = "9693703723@fam"

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

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(contentPadding)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 16.dp)) {
            IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, "Back") }
            Spacer(Modifier.width(8.dp))
            Text("About", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        }
        
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
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/Hotaro26"))
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

@Composable
fun StoryScreen(onBack: () -> Unit, contentPadding: PaddingValues) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(contentPadding)
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 16.dp)) {
            IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, "Back") }
            Spacer(Modifier.width(8.dp))
            Text("Story", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        }
        
        Text(
            "I used to open YouTube to watch educational lectures and study material, but the algorithm and endless Shorts would always get me hooked and distracted. Hours would pass by without any real work getting done.\n\nI built Fookus Tube to eliminate those distractions—especially during intense times like JEE prep. It's designed to keep you focused on what you actually intended to watch, and allows you to easily save those important lectures for offline viewing when there's no Wi-Fi.\n\nFookus Tube is your tool to take back control of your time.",
            style = MaterialTheme.typography.bodyLarge,
            modifier = Modifier.padding(16.dp)
        )
    }
}
