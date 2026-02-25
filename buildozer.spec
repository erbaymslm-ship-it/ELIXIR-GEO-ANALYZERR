[app]

# (str) Başlık – uygulamanızın adı (Android'de görünen isim)
title = ELIXIR TECHNOLOGY

# (str) Paket adı (Java paket ismi gibi, genelde ters domain)
package.name = elixir

# (str) Paket domain (genelde şirket/kişi domaini)
package.domain = com.elixir.technology

# (str) Kaynak kodunuzun bulunduğu klasör
source.dir = src

# (list) Kaynak olarak dahil edilecek dosya uzantıları (virgülle ayırın)
source.include_exts = py,png,jpg,kv,atlas,txt,ino,wav

# (str) Uygulama sürümü
version = 0.1

# (str) Sürüm numarasının alınacağı dosya (opsiyonel)
version.filename = %(source.dir)s/main.py

# (list) Gereksinimler (Python paketleri)
requirements = python3,kivy==2.3.0,pillow,pyjnius,plyer,android

# (str) Uygulamanızın giriş noktası (ana Python dosyası)
source.main = src/main.py

# (str) Ön yükleme ekranı (splash screen) resmi
presplash.filename = %(source.dir)s/assets/splash.png

# (str) Uygulama ikonu
icon.filename = %(source.dir)s/assets/icon.png

# (str) Ekran yönü (portrait, landscape, vs.)
orientation = portrait

# (bool) Tam ekran modu (0 veya 1)
fullscreen = 0

# (list) Dahil edilecek ekstra kütüphane dosyaları (örn. arka plan servisleri için)
# android.add_src =

# (list) Java dosyaları (örn. özel aktiviteler) – gerekirse ekleyin
# android.add_src =

# (str) Android için hedef SDK API seviyesi
android.api = 33

# (str) Android için minimum SDK API seviyesi
android.minapi = 21

# (str) Kullanılacak NDK sürümü (r25b önerilir)
android.ndk = 25b

# (str) Kullanılacak SDK sürümü (genelde api ile aynı)
android.sdk = 30

# (list) Android izinleri (izinler virgülle ayrılır)
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_SCAN,BLUETOOTH_CONNECT,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# (str) Gradle bağımlılıkları (örn. Google Play Services)
android.gradle_dependencies = com.google.android.gms:play-services-location:21.0.1

# (str) Java sürümü (genelde 8 veya 11)
android.java_version = 11

# (str) Android manifestine eklenecek özel özellikler (feature)
android.manifest = <uses-feature android:name="android.hardware.bluetooth" android:required="true" />

# (str) Android manifestine uygulama etiketine eklenecek ekstra parametreler
android.extra_manifest_application_arguments = android:allowBackup="true" android:theme="@style/Theme.AppCompat.Light"

# (bool) Ant yerine Gradle kullan (önerilir)
android.gradle = 1

# (bool) Uygulamayı hata ayıklama modunda derle (logcat'te detaylı çıktı için)
android.debug = 1

# (str) APK çıktı klasörü (genelde ./bin/)
android.output = ./bin/

# (str) Arşiv adı (APK adı) – isteğe bağlı
android.arch = armeabi-v7a,arm64-v8a

[buildozer]

# (int) Log seviyesi (1-3 arası, 2 önerilir)
log_level = 2

# (bool) Kök dizinde çalıştırıldığında uyarı versin mi?
warn_on_root = 1
