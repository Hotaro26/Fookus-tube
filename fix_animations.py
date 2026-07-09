import re

path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"

with open(path, "r") as f:
    content = f.read()

# 1. Remove bouncy touch effect from pills
pills_bouncy = """            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                val historyInteraction = remember { MutableInteractionSource() }
                val historyPressed by historyInteraction.collectIsPressedAsState()
                val historyScale by animateFloatAsState(if (historyPressed) 0.8f else 1.0f, animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy))
                
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "History" },
                    label = { Text("History") },
                    modifier = Modifier.scale(historyScale),
                    interactionSource = historyInteraction
                )
                
                val offlineInteraction = remember { MutableInteractionSource() }
                val offlinePressed by offlineInteraction.collectIsPressedAsState()
                val offlineScale by animateFloatAsState(if (offlinePressed) 0.8f else 1.0f, animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy))
                
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "Offline" },
                    label = { Text("Offline") },
                    modifier = Modifier.scale(offlineScale),
                    interactionSource = offlineInteraction
                )
            }"""

pills_flat = """            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "History" },
                    label = { Text("History") }
                )
                FilterChip(
                    selected = false,
                    onClick = { selectedFilter = "Offline" },
                    label = { Text("Offline") }
                )
            }"""

if pills_bouncy in content:
    content = content.replace(pills_bouncy, pills_flat)


# 2. Add AnimatedContent for the whole tab layout
# We will find `    if (selectedFilter != "Search") {` and `    Box(modifier = Modifier.fillMaxSize()) {`
# We need to wrap them properly.

# Let's do a regex to capture everything from `if (selectedFilter != "Search") {` up to the end of `NewPipeTab` block.
# Actually, it's easier to find the specific markers.

split_marker_1 = "    if (selectedFilter != \"Search\") {"
split_marker_2 = "        return\n    }\n\n    Box(modifier = Modifier.fillMaxSize()) {"

if split_marker_1 in content and split_marker_2 in content:
    part1, rest = content.split(split_marker_1, 1)
    page_block, part3 = rest.split(split_marker_2, 1)
    
    # page_block is the Scaffold for History/Offline
    # part3 is the Box for Search
    # We need to find the end of part3 (which is the end of the NewPipeTab function).
    # Since NewPipeTab is the last function or we can just count braces.
    
    # Actually, part3 ends with a single `}` for the NewPipeTab function.
    # Let's find the last `}` in part3.
    
    last_brace_idx = part3.rfind("}")
    search_block = part3[:last_brace_idx]
    after_func = part3[last_brace_idx:]
    
    # Replace `selectedFilter` with `currentFilter` inside page_block and search_block
    page_block = page_block.replace("selectedFilter", "currentFilter")
    # Actually, in search_block, selectedFilter is used for `selectedFilter = "History"`, we shouldn't change assignment!
    # Wait, `selectedFilter == "History"` vs `selectedFilter = "History"`.
    page_block = page_block.replace("currentFilter == \"History\"", "currentFilter == \"History\"")
    page_block = page_block.replace("currentFilter == \"Offline\"", "currentFilter == \"Offline\"")
    # The title Text(selectedFilter) -> Text(currentFilter)
    page_block = page_block.replace("Text(selectedFilter)", "Text(currentFilter)")
    
    # We don't need to change `selectedFilter = "Search"` because we want to update the actual state!
    page_block = page_block.replace("currentFilter = \"Search\"", "selectedFilter = \"Search\"")
    
    animated_wrapper = f"""    androidx.compose.animation.AnimatedContent(targetState = selectedFilter, label = "filter_transition") {{ currentFilter ->
        if (currentFilter != "Search") {{
{page_block}        }} else {{
            Box(modifier = Modifier.fillMaxSize()) {{
{search_block}            }}
        }}
    }}
{after_func}"""

    content = part1 + animated_wrapper

with open(path, "w") as f:
    f.write(content)

print("Applied page transition animation and reverted bouncy pills")
