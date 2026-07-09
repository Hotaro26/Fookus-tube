import os

newpipe_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"
with open(newpipe_path, "r") as f:
    np_content = f.read()

if "import androidx.compose.foundation.shape.RoundedCornerShape" not in np_content:
    np_content = np_content.replace(
        "import androidx.compose.foundation.shape.CircleShape",
        "import androidx.compose.foundation.shape.CircleShape\nimport androidx.compose.foundation.shape.RoundedCornerShape"
    )

with open(newpipe_path, "w") as f:
    f.write(np_content)

print("Added RoundedCornerShape import")
