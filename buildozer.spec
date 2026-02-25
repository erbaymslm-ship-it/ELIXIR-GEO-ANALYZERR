[app]

# (str) Başlık (uygulama adı)
title = ELIXIR TECHNOLOGY

# (str) Paket adı (Android için paket ismi)
package.name = elixir

# (str) Paket domain (genellikle ters domain)
package.domain = com.elixir.technology

# (str) Kaynak kodun bulunduğu dizin
source.dir = src

# (list) Kaynak dosya uzantıları (derleme sırasında dahil edilecek)
source.include_exts = py,png,jpg,kv,atlas,txt,ino,wav

# (str) Uygulama sürümü
version = 0.1

# (str) Sürüm numarasını almak için dosya (opsiyonel)
# version.filename = %(source.dir)s/main.py

# (list) Gereksinimler (Python paketleri)
requirements = python3,kivy==2.3.0,pillow,pyjnius,plyer,android

# (str) Presplash (açılış ekranı) resmi
presplash.filename = %(source.dir)s/assets/splash.png

# (str) Uygulama ikonu
icon.filename = %(source.dir)s/assets/icon.png

# (str) Ekran yönü (portrait, landscape, etc.)
orientation = portrait

# (bool) Tam ekran modu
fullscreen = 0

# (list) İzinler (Android için)
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_SCAN,BLUETOOTH_CONNECT,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# (str) Android API seviyesi (hedef SDK)
android.api = 33

# (str) Minimum Android API seviyesi
android.minapi = 21

# (str) NDK sürümü
android.ndk = 25b

# (str) SDK sürümü (build tools vs.)
android.sdk = 30

# (bool) Gradle kullan (önerilir)
android.gradle = 1

# (list) Gradle bağımlılıkları (opsiyonel, konum için gerekli değil ama kalabilir)
android.gradle_dependencies = com.google.android.gms:play-services-location:21.0.1

# (str) Java versiyonu
android.java_version = 11

# (bool) Ant yerine Gradle kullan
android.use_gradle = True

# (str) Android manifest'e eklenecek özel feature
android.manifest = <uses-feature android:name="android.hardware.bluetooth" android:required="true" />

# (str) Manifest'e eklenecek ekstra uygulama parametreleri
android.extra_manifest_application_arguments = android:allowBackup="true" android:theme="@style/Theme.AppCompat.Light"

# (bool) Uygulama hata ayıklama modunda olsun mu? (genelde evet)
android.debug = True

[buildozer]

# (int) Log seviyesi (0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR, 4=CRITICAL)
log_level = 2

# (bool) Kök dizinde çalıştırma uyarısı
warn_on_root = 1

# (str) arşiv formatı (tar.gz veya zip)
archive_format = tar.gz
