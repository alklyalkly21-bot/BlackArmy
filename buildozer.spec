[app]
title = BlackArmy Lab v3
package.name = blackarmylab
package.domain = org.lab
source.dir = .
source.include_exts = py,json,png,jpg,jpeg,kv,atlas
version = 3.0.0
requirements = python3,kivy==2.3.1,requests
orientation = portrait
fullscreen = 0

# Network only. Android sensitive data stays behind user-facing system UI.
android.permissions = INTERNET
android.api = 35
android.minapi = 23

[buildozer]
log_level = 2
warn_on_root = 1
