import os

gabi_screen = "/home/hotaro/Projects/gabi/app/src/androidMain/kotlin/com/material/downloader/ui/DownloaderScreen.kt"
fookus_screen = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"

with open(gabi_screen, "r") as f:
    content = f.read()

settings_idx = content.find("@Composable\nfun SettingsTab")
if settings_idx != -1:
    logs_tab = content.find("@Composable\nfun LogsTab")
    settings_code = content[settings_idx:logs_tab].replace("com.material.downloader", "com.fookus.tube")
    
    with open(fookus_screen, "a") as f:
        f.write("\n\n" + settings_code)

print("SettingsTab imported!")
