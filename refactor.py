import os
import shutil
import re

root_dir = "/home/hotaro/Projects/fookus-tube"

def read_file(path):
    with open(path, "r") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)

# 1. Update build.gradle.kts
build_gradle_path = os.path.join(root_dir, "app/build.gradle.kts")
build_gradle = read_file(build_gradle_path)
build_gradle = build_gradle.replace('id("com.chaquo.python")', "")
build_gradle = build_gradle.replace('id("com.google.devtools.ksp") version "1.9.22-1.0.17"', "")
build_gradle = re.sub(r'val ktor_version.*?\n.*?ktor-client-logging.*?\n', '', build_gradle, flags=re.DOTALL)
build_gradle = re.sub(r'val room_version.*?\n.*?room-ktx.*?\n', '', build_gradle, flags=re.DOTALL)
build_gradle = build_gradle.replace('namespace = "com.material.downloader"', 'namespace = "com.fookus.tube"')
build_gradle = build_gradle.replace('applicationId = "com.material.downloader"', 'applicationId = "com.fookus.tube"')
build_gradle = re.sub(r'ndk\s*\{.*?\}', '', build_gradle, flags=re.DOTALL)
build_gradle = re.sub(r'chaquopy\s*\{.*?\}', '', build_gradle, flags=re.DOTALL)
build_gradle = re.sub(r'dependencies\s*\{\s*add\("kspAndroid".*?\)\s*\}', '', build_gradle, flags=re.DOTALL)
write_file(build_gradle_path, build_gradle)

# 2. Rename package directories
def move_package(src_pkg, dst_pkg):
    for root, dirs, files in os.walk(root_dir):
        if ".git" in root or "build" in root:
            continue
        src_path = os.path.join(root, src_pkg.replace(".", "/"))
        if os.path.exists(src_path):
            dst_path = os.path.join(root, dst_pkg.replace(".", "/"))
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.move(src_path, dst_path)

move_package("com.material.downloader", "com.fookus.tube")

# 3. Replace all package references in code
for root, dirs, files in os.walk(root_dir):
    if ".git" in root or "build" in root:
        continue
    for file in files:
        if file.endswith((".kt", ".xml", ".pro", ".kts", ".md")):
            path = os.path.join(root, file)
            content = read_file(path)
            if "com.material.downloader" in content or "Gabi" in content:
                content = content.replace("com.material.downloader", "com.fookus.tube")
                content = content.replace("Gabi", "FookusTube")
                write_file(path, content)

print("Refactoring complete.")
