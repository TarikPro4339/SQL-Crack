# SQL Crack v1.0.1 — Yenilikler

**Yapımcı:** TarikPro43391  
**Sürüm:** v1.0.1  
**Tür:** Yerel, eğitim amaçlı SQL güvenlik simülatörü

## Yeni
- SQL CRACK ASCII başlıklı, turkuaz CMD introsu ve dört aşamalı başlatma kontrolü.
- Tek tıkla **Son Testi Tekrarla** düğmesi (girdiler yalnızca sekme açıkken bellekte tutulur).
- **Terminali TXT indir** özelliği.
- **Otomatik yenileme** aç/kapat kontrolü.
- Arayüzde sürüm yeniliklerini gösteren özel panel.

## Düzeltilenler
- Eksik Python/proje dosyalarında anlaşılırlığı artırılmış CMD uyarıları.
- Önceki günlükler çok büyüdüğünde gereksiz belleğe yüklenmesinin önlenmesi.
- Log kırpma sırasında dosya bütünlüğü için güvenli dosya değiştirme.
- Bozuk günlük satırlarıyla çalışırken hata toleransı.
- İstek boyutu ve JSON içerik türü denetimlerinin sıkılaştırılması.
- İstek sonrası hata durumunda daha anlamlı JSON hata yanıtları.
- Son testin tekrarından sonra durum ve raporların güncellenmesi.

## Kullanım
1. ZIP dosyasını tamamen çıkarın.
2. Windows'ta `SQL Crack Start.bat` dosyasını çalıştırın (Python 3.9+ gereklidir).
3. CMD penceresindeki sunucu adresi tarayıcıda açılır.
4. `data/events.jsonl` içinde logları; `data/dumps/` içinde **sahte eğitim** dump dosyalarını bulabilirsiniz.

**Güvenlik:** Gerçek SQL enjeksiyonu çalıştırmaz, dış hedefe ağ isteği göndermez ve gerçek veritabanlarından dump almaz.

- CMD açılışı kullanıcı tarafından seçilen ASCII SQL CRACK introsuna güncellendi (`assets/cmd_intro.txt`). WAF/erişim satırları sadece kurgusal görsel efekttir.

## Yeni başlangıç deneyimi
- **Start.py:** Ana giriş dosyası.
- Matrix tarzında akan karakterler ve sıralı harf-harf terminal komutları.
- `SQL Crack Start.bat` doğrudan `Start.py` çağırır.
- ZIP içerisindeki ana klasörün adı **SQL Crack v1.0.1**.
- Komutlar yalnızca görsel simülasyondur.
