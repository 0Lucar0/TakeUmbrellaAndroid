[app]
title = Возьми зонтик
package.name = takeumbrella
package.domain = org.example

source.dir = .
source.include_exts = py,kv,png,jpg,atlas,json,ttf

version = 0.1.0

requirements = python3,kivy,plyer,pyjnius
orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_COARSE_LOCATION,ACCESS_FINE_LOCATION,ACCESS_BACKGROUND_LOCATION,POST_NOTIFICATIONS,RECEIVE_BOOT_COMPLETED,WAKE_LOCK

android.api = 34
android.minapi = 24
android.ndk_api = 24
android.sdk_build_tools = 34.0.0
android.sdk_path = /usr/local/lib/android/sdk

android.services = umbrella_service:service/main.py

android.enable_androidx = 1

[buildozer]
log_level = 2

