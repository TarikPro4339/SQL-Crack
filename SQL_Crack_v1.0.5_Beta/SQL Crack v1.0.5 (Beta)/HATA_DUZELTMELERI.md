# SQL Crack v1.0.5 (Beta) — Hata Düzeltmeleri

Sürüm numarası **v1.0.5 (Beta)** olarak korunmuştur. 32 özellik, Matrix introsu ve `SQL Crack Start.bat` yerindedir.

## Düzeltilenler
- Eski veya bozuk JSONL olayları artık rapor ve güvenlik API ekranlarını çökertmez.
- Çakışan web paneli yenilemeleri güncel verileri yanlışlıkla ezmez.
- HTTP istekleri zaman aşımında anlaşılır bir mesaj gösterir.
- Simülasyon ve izinli kontrol aynı anda başlatılamaz.
- Günlük temizleme ve sahte dump silme işlemlerindeki izin hataları yakalanır.
- Günlük kaydı başarısızsa yeni üretilen sentetik dump silinir.
- Silinen dosyaların listeleme sırasında neden olduğu olası yarış durumu giderildi.
- `Start.py --no-animation` harf harf yazma gecikmelerini de kapatır.
- Python sürümü introdan önce doğrulanır.

## Doğrulama
- `python -m unittest discover -s tests -v`: **37/37 başarılı**
- Python derleme ve `node --check app.js`: başarılı
- Gerçek `Start.py --no-animation` başlatması ve yerel HTTP API smoke testi: başarılı
- Windows CMD ve Chromium görsel testi bu Linux ortamında doğrulanamamıştır.

**Not:** İzinli HTTP kontrolleri yalnızca zararsız GET istekleri gönderir. SQL saldırısı, veri toplama veya gerçek dump alma işlemi bulunmaz.

## Ek düzeltmeler (v1.0.5 (Beta))
- İstemciye gösterilen, API yanıtlarında ve HTTP başlıklarında bulunan sürüm kimlikleri eşitlendi: `v1.0.5 (Beta)`.
- Günlük dosyası erişilemezse `/api/state`, `/api/reports`, `/api/safety` ve `/api/export` artık 500 JSON yanıtı verir.
- Statik arayüz dosyası okunamazsa bağlantı kopmak yerine açık hata mesajı verilir.
- Tüm sürüm numaralarının tutarlılığını ve yeni hata yanıtlarını doğrulayan testler eklendi.
