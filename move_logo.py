import re

newpipe_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"

with open(newpipe_path, "r") as f:
    content = f.read()

# 1. Remove the old logo logic from the bottom
old_logo = """                if (results.isEmpty()) {
                    Spacer(modifier = Modifier.fillMaxHeight(0.2f))
                    Icon(
                        painter = androidx.compose.ui.res.painterResource(android.R.drawable.ic_media_play),
                        contentDescription = "YouTube",
                        modifier = Modifier.size(72.dp).padding(bottom = 16.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Text(
                        "YouTube Search",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                    )
                } else {"""

content = content.replace(old_logo, "                if (results.isEmpty()) {\n                    // Empty state handled above\n                } else {")

# 2. Add the logo above the OutlinedTextField
new_logo = """            if (isListEmpty) {
                Icon(
                    painter = androidx.compose.ui.res.painterResource(android.R.drawable.ic_media_play),
                    contentDescription = "Fookus Tube",
                    modifier = Modifier.size(72.dp).padding(bottom = 16.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
                Text(
                    "Fookus Tube",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(24.dp))
            }
            
            OutlinedTextField("""

content = content.replace("            OutlinedTextField(", new_logo)

with open(newpipe_path, "w") as f:
    f.write(content)
