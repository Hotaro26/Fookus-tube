import re

path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"

with open(path, "r") as f:
    content = f.read()

# Replace Modifier.fillMaxSize(), with Modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)), inside AsyncImage definitions.
old_modifier = "modifier = Modifier.fillMaxSize(),"
new_modifier = "modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(8.dp)),"

# Wait, checking if I need to import clip.
if "import androidx.compose.ui.draw.clip" not in content:
    content = content.replace("import androidx.compose.ui.Alignment", "import androidx.compose.ui.Alignment\nimport androidx.compose.ui.draw.clip")

content = content.replace(old_modifier, new_modifier)

with open(path, "w") as f:
    f.write(content)

print("Applied rounded corners to thumbnails")
