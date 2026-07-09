import re

path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"

with open(path, "r") as f:
    content = f.read()

# We want to remove the logo from the Offline sections.
bad_logo = """            if (isListEmpty) {
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
            
            """

# Find all occurrences of bad_logo
occurrences = content.count(bad_logo)

# Replace only the first 3 occurrences (because the 4th is the good one in the search bar).
# Wait, let's just replace all of them with empty string, and then put the good one back before OutlinedTextField of search bar!

content = content.replace(bad_logo, "")

good_logo = """            if (isListEmpty) {
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
            
            OutlinedTextField(
                value = query,"""

content = content.replace("            OutlinedTextField(\n                value = query,", good_logo)

with open(path, "w") as f:
    f.write(content)

print("Fixed the logo duplication issue")
