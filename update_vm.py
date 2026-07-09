import os

vm_path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/DownloaderViewModel.kt"
with open(vm_path, "r") as f:
    vm_content = f.read()

terminal_theme_code = """
enum class TerminalTheme(val displayName: String, val background: Long, val header: Long, val text: Long) {
    HACKER("Hacker Green", 0xFF0D1117, 0xFF161B22, 0xFF00FF00),
    DRACULA("Dracula", 0xFF282A36, 0xFF44475A, 0xFFF8F8F2),
    MONOKAI("Monokai", 0xFF272822, 0xFF3E3D32, 0xFFF8F8F2),
    SOLARIZED("Solarized Dark", 0xFF002B36, 0xFF073642, 0xFF839496),
    UBUNTU("Ubuntu", 0xFF300A24, 0xFF5E2750, 0xFFFFFFFF)
}
"""

if "enum class TerminalTheme" not in vm_content:
    vm_content = vm_content + "\n" + terminal_theme_code

# Update ViewModel state
if "val consoleLogs" not in vm_content:
    vm_content = vm_content.replace(
        "val terminalTheme = mutableStateOf(0)",
        "val terminalTheme = mutableStateOf(TerminalTheme.HACKER)\n    val consoleLogs = androidx.compose.runtime.mutableStateListOf<String>()\n    fun clearConsole() { consoleLogs.clear() }"
    )
    vm_content = vm_content.replace(
        "fun updateTerminalTheme(theme: Int)",
        "fun updateTerminalTheme(theme: TerminalTheme)"
    )
    
# Mock Download function
mock_download = """
    fun startMockDownload(video: SavedVideo, quality: String, format: String) {
        androidx.lifecycle.viewModelScope.launch(kotlinx.coroutines.Dispatchers.IO) {
            consoleLogs.add("fookus@tube: ~$ yt-dlp -f $quality $format ${video.url}")
            kotlinx.coroutines.delay(500)
            consoleLogs.add("[youtube] Extracting URL: ${video.url}")
            kotlinx.coroutines.delay(1000)
            consoleLogs.add("[youtube] Downloading video info...")
            for (i in 1..10) {
                kotlinx.coroutines.delay(300)
                consoleLogs.add("[download] ${i * 10}% of 15.00MiB at 5.00MiB/s ETA 00:02")
            }
            consoleLogs.add("[download] Destination: /storage/emulated/0/Download/${video.title}.mp4")
            kotlinx.coroutines.delay(500)
            consoleLogs.add("[ffmpeg] Merging formats...")
            kotlinx.coroutines.delay(500)
            consoleLogs.add("Download completed successfully!")
            
            withContext(kotlinx.coroutines.Dispatchers.Main) {
                addToOffline(video)
            }
        }
    }
"""

if "startMockDownload" not in vm_content:
    vm_content = vm_content.replace(
        "fun addToOffline(video: SavedVideo) {",
        mock_download + "\n    fun addToOffline(video: SavedVideo) {"
    )

if "import kotlinx.coroutines.withContext" not in vm_content:
    vm_content = vm_content.replace("import kotlinx.coroutines.launch", "import kotlinx.coroutines.launch\nimport kotlinx.coroutines.withContext")

with open(vm_path, "w") as f:
    f.write(vm_content)
    
print("Updated ViewModel")
