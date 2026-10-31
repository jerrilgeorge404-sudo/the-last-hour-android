[app]

# (str) Title of your application
title = The Last Hour: Project Echo

# (str) Package name
package.name = thelasthour

# (str) Package domain (needed for android/ios packaging)
package.domain = org.projectecho

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,ttf,fs,vs,wav,ogg,mp3,json,txt

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,shaders/*,audio_cache/*

# (str) Application versioning (method 1)
version = 1.87

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pyray,cffi,pillow,numpy

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen to the user
fullscreen = 1

# (list) Permissions
android.permissions = WAKE_LOCK, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (list) The Android architectures to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk or default).
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug when possible)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
