import os
import re

file_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"

with open(file_path, "r") as f:
    content = f.read()

# 1. Update the tabs in DownloaderScreen
# Replace the NavigationBar items
nav_bar_regex = re.compile(r'NavigationBar\(\s*containerColor = Color\.Transparent,\s*tonalElevation = 0\.dp\s*\)\s*\{.*?\}(?=\s*\}\s*\},)', re.DOTALL)

new_nav_bar = """NavigationBar(
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
                    }"""

content = nav_bar_regex.sub(new_nav_bar, content)

# Replace NavigationRail items
nav_rail_regex = re.compile(r'NavigationRail\(\s*containerColor = Color\.Transparent\s*\)\s*\{.*?\}(?=\s*\}\s*Box\()', re.DOTALL)

new_nav_rail = """NavigationRail(
                        containerColor = Color.Transparent
                    ) {
                        Spacer(modifier = Modifier.weight(1f))
                        NavigationRailItem(
                            selected = selectedTab == 0,
                            onClick = { selectedTab = 0 },
                            icon = { Icon(Icons.Default.PlayArrow, null) },
                            label = { Text("Home") }
                        )
                        NavigationRailItem(
                            selected = selectedTab == 1,
                            onClick = { selectedTab = 1 },
                            icon = { Icon(Icons.Default.Settings, null) },
                            label = { Text("Settings") }
                        )
                        Spacer(modifier = Modifier.weight(1f))
                    }"""
content = nav_rail_regex.sub(new_nav_rail, content)

# Replace the AnimatedContent for the tabs
anim_content_regex = re.compile(r'AnimatedContent\(targetState = selectedTab.*?\).*?\}\s*\}\s*\}\s*\}\s*\}', re.DOTALL)

new_anim_content = """AnimatedContent(targetState = selectedTab, label = "tab_transition") { targetTab ->
                        when (targetTab) {
                            0 -> NewPipeTab(viewModel)
                            1 -> SettingsTab(viewModel, innerPadding)
                        }
                    }
                }
            }
        }
    }"""
content = anim_content_regex.sub(new_anim_content, content)

# Find and remove MainDownloaderTab and LogsTab
# We will just split the file at "fun MainDownloaderTab" and keep the beginning
main_tab_index = content.find("@Composable\nfun MainDownloaderTab")
if main_tab_index != -1:
    content_top = content[:main_tab_index]
    # Find SettingsTab
    settings_tab_index = content.find("@Composable\nfun SettingsTab")
    logs_tab_index = content.find("@Composable\nfun LogsTab")
    
    content_settings = ""
    if settings_tab_index != -1 and logs_tab_index != -1:
        content_settings = content[settings_tab_index:logs_tab_index]
    elif settings_tab_index != -1:
        content_settings = content[settings_tab_index:]
        
    content = content_top + "\n" + content_settings

with open(file_path, "w") as f:
    f.write(content)

print("DownloaderScreen.kt refactored.")
