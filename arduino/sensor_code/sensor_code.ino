/*
ELIXIR TECHNOLOGY
Arduino Sensör Kodu - Verilen kod aynen kullanılacak
*/

// Sensör pin tanımlamaları
const int sensorPin = A0;  // Analog sensör girişi

void setup() {
  // Seri haberleşme başlat (9600 baud)
  Serial.begin(9600);
  
  // Başlangıç mesajı
  Serial.println("ELIXIR SENSOR READY");
}

void loop() {
  // Sensörden analog değer oku (0-1023)
  int sensorValue = analogRead(sensorPin);
  
  // Değeri seri porta gönder (integer olarak)
  Serial.println(sensorValue);
  
  // Kısa bekleme
  delay(100);
}
