import re

# 1. Update AndroidManifest.xml
manifest_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/AndroidManifest.xml"
with open(manifest_path, "r") as f:
    manifest_content = f.read()

if 'android:enableOnBackInvokedCallback="true"' not in manifest_content:
    manifest_content = manifest_content.replace(
        '<application\n',
        '<application\n        android:enableOnBackInvokedCallback="true"\n'
    )
    with open(manifest_path, "w") as f:
        f.write(manifest_content)


# 2. Add BackHandler to NewPipeTab.kt
np_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"
with open(np_path, "r") as f:
    np_content = f.read()

# Make sure imports are present
if "import androidx.activity.compose.BackHandler" not in np_content:
    np_content = np_content.replace("import androidx.compose.ui.Modifier", "import androidx.compose.ui.Modifier\nimport androidx.activity.compose.BackHandler")

target_marker = 'if (currentFilter != "Search") {'
replacement = """if (currentFilter != "Search") {
            BackHandler {
                selectedFilter = "Search"
            }"""

if "BackHandler {" not in np_content:
    np_content = np_content.replace(target_marker, replacement, 1)
    with open(np_path, "w") as f:
        f.write(np_content)


# 3. Add BackHandler to DownloaderScreen.kt
ds_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"
with open(ds_path, "r") as f:
    ds_content = f.read()

if "import androidx.activity.compose.BackHandler" not in ds_content:
    ds_content = ds_content.replace("import androidx.compose.ui.Modifier", "import androidx.compose.ui.Modifier\nimport androidx.activity.compose.BackHandler")

target_marker2 = "AnimatedContent(targetState = selectedTab, label = \"tab_transition\") { targetTab ->"
replacement2 = """if (selectedTab == 1) {
            BackHandler {
                selectedTab = 0
            }
        }
        
        AnimatedContent(targetState = selectedTab, label = "tab_transition") { targetTab ->"""

if "BackHandler {" not in ds_content:
    ds_content = ds_content.replace(target_marker2, replacement2, 1)
    with open(ds_path, "w") as f:
        f.write(ds_content)

print("Applied BackHandler and enableOnBackInvokedCallback")
