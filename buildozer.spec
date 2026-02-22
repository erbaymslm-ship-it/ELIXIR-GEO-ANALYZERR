[app]
title = ELIXIR TECHNOLOGY
package.name = elixir
package.domain = com.elixir.technology

source.dir = src
source.include_exts = py,png,jpg,kv,atlas,txt,ino

version = 0.1
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

requirements = python3,kivy==2.1.0,numpy==1.22.4,pyjnius,android,pyopenssl

presplash.filename = %(source.dir)s/assets/splash.png
icon.filename = %(source.dir)s/assets/icon.png

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0

fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 33
minapi = 21
ndk = 25b
sdk = 30

# Android izinleri
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_SCAN,BLUETOOTH_CONNECT,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Google Play Services (Bluetooth için)
android.gradle_dependencies = 'com.google.android.gms:play-services-location:21.0.1'

# Java sürümü
android.java_version = 11

# Manifest özellikleri
android.manifest = <uses-feature android:name="android.hardware.bluetooth" android:required="true" />
android.extra_manifest_application_arguments = android:allowBackup="true" android:theme="@style/Theme.AppCompat.Light"

# Gradle özellikleri
android.gradle_task = assembleRelease
android.add_src =

# APK imzalama (release build için)
android.release_artifact = True
android.ndk_path = 
android.sdk_path =

[requirements]
# iOS requirements
ios.kivy_version = 2.1.0