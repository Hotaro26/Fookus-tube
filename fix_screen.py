import os
import re

screen_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderScreen.kt"

with open(screen_path, "r") as f:
    content = f.read()

# Fix verticalScroll import
if "import androidx.compose.foundation.verticalScroll" not in content:
    content = content.replace("import androidx.compose.foundation.horizontalScroll", "import androidx.compose.foundation.horizontalScroll\nimport androidx.compose.foundation.verticalScroll")

# Fix Uri assignment
content = content.replace("viewModel.selectedFolderUri.value = uri.toString()", "viewModel.selectedFolderUri.value = uri")

# Remove TerminalTheme section
# Finding "Terminal Appearance"
start_idx = content.find('Text("Terminal Appearance"')
if start_idx != -1:
    # Find the nearest Card { before it
    card_start = content.rfind("item {", 0, start_idx)
    # Find the next item { after it
    card_end = content.find("item {", start_idx)
    if card_end == -1:
        # It's the last item
        card_end = content.rfind("}")
        # Need to be careful. Let's just remove the block with regex or string replacement.
    
    # We can just replace TerminalTheme.entries.forEach with nothing, but it will leave broken compose UI.
    pass

# Alternatively, just remove the whole TerminalTheme block
term_regex = re.compile(r'item\s*\{\s*Card\s*\{\s*Column\(Modifier\.padding\(16\.dp\)\)\s*\{\s*Text\("Terminal Appearance".*?\}\s*\}\s*\}\s*\}', re.DOTALL)
content = term_regex.sub("", content)

with open(screen_path, "w") as f:
    f.write(content)

print("Fixed DownloaderScreen.kt")
