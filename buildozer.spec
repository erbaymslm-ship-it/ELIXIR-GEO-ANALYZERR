[app]

title = ELIXIR TECHNOLOGY
package.name = elixir
package.domain = com.elixir.technology

source.dir = src
source.include_exts = py,png,jpg,kv,atlas,txt,ino

version = 0.1
version.filename = %(source.dir)s/main.py

requirements = python3,kivy==2.3.0,pillow,pyjnius,plyer

presplash.filename = %(source.dir)s/assets/splash.png
icon.filename = %(source.dir)s/assets/icon.png

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 33
minapi = 21
ndk = 25b
sdk = 30

# İzinler (Android 12+ için hepsi)
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION

# Google Play Services (isteğe bağlı, konum için)
android.gradle_dependencies = com.google.android.gms:play-services-location:21.0.1

# Java sürümü
android.java_version = 11

# Bluetooth özelliğini manifest'e ekle
android.manifest = <uses-feature android:name="android.hardware.bluetooth" android:required="true" />

# (Eski hatalı satırı kaldırdım)
# android.extra_manifest_application_arguments = ... (sil)
