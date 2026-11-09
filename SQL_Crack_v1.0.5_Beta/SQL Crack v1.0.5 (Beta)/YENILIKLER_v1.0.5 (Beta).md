# SQL Crack v1.0.5 (Beta) — Yenilikler

- İzinli hedefler için sınırlı ve zararsız GET kontrolü eklendi.
- Her kontrol yeni rastgele parametre adı ve değeri üretir (SQL payload değildir).
- Hedefler `scope.json` ile kesin URL üzerinden sınırlandırılır.
- Hız sınırı: çalıştırma başına en fazla 3 istek, toplamda dakikada en fazla 6 istek; aralarında en az 0,8 saniye.
- Harici adreslerde HTTPS ve genel erişimli IP gereklidir.
- İstekler yanıt gövdesini okumaz ve yönlendirmeleri izlemez.
- Gerçek SQL saldırısı, veri çekme veya güvenlik duvarı atlatma uygulanmaz.
- Eski Matrix introsu, bat başlatıcısı, log kayıtları ve sentetik dump sistemi korunmuştur.
- Versiyon: `v1.0.5 (Beta)`; yapımcı: `TarikPro43391`.

## v1.0.5 (Beta) — sürüm numarası değişmeden eklenen 3 özellik

1. **Sunucu Sağlık Monitörü:** Uptime, yanıt adedi, son 200 yerel HTTP yanıtında ortalama süre ve 5xx hataları (`/api/monitor`).
2. **Gelişmiş Test Raporları:** Son 24 saat/önceki 24 saat kıyası; uyarı, başarı yüzdesi, ortalama gecikme ve senaryo sıralaması (`/api/reports`).
3. **Akıllı Güvenlik Kontrolü:** İzinli URL sayısı, kapsam/limit engelleri, kalan dakika kotası ve art arda başarısızlık uyarıları (`/api/safety`).

Bu özellikler salt okunur analizdir ve mevcut izne dayalı zararsız HTTP kontrolünün kapsamını genişletmez.
