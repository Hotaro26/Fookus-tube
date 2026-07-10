with open("app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderViewModel.kt") as f:
    text = f.read()

depth = 0
for i, line in enumerate(text.splitlines(), 1):
    prev_depth = depth
    in_string = False
    escape = False
    for char in line:
        if escape:
            escape = False
            continue
        if char == '\\':
            escape = True
            continue
        if char == '"':
            in_string = not in_string
        if not in_string:
            if char == '{': depth += 1
            elif char == '}': depth -= 1
    if depth != prev_depth and (depth == 0 or depth == 1 or depth == 2 or i > 580):
        print(f"Line {i}: {line.strip()} (depth {prev_depth} -> {depth})")
print(f"Final depth: {depth}")
