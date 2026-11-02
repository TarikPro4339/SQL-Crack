# 💜 SQL Crack — v1.0.1

<p align="center">
  <img src="assets/sql-crack-logo.png" alt="SQL Crack logosu" width="170">
</p>

<p align="center">
  <strong>Neon hacker arayüzlü, eğitim amaçlı SQL güvenlik testi simülatörü.</strong><br>
  25 temel özellik • Canlı terminal • Kalıcı günlükler • Sahte SQL dump • Windows CMD başlatıcısı
</p>

> [!IMPORTANT]
> **SQL Crack gerçek bir SQL saldırı aracı değildir.** Gerçek web sitelerine SQL enjeksiyonu uygulamaz, veritabanlarına bağlanmaz veya veri sızdırmaz. Testler tamamen **simülasyon** olarak çalışır; oluşturulan SQL dump dosyaları **sentetik (sahte) örnek veriler** içerir.

## 🚀 v1.0.1 güncellemesi

- **Matrix tarzı CMD açılışı:** `Start.py` üzerinde yeşil akan karakterler, harf harf yazılan demo komutları ve özel SQL CRACK ASCII introsu; efektler yalnızca görseldir.
- **Son Testi Tekrarla:** Bir önceki demo senaryosunu tekrar çalıştır.
- **Terminal TXT İndir:** Terminal mesajlarını metin dosyası olarak kaydet.
- **Otomatik Yenileme Kontrolü:** Arka planda log yenilemesini durdur veya devam ettir.
- **Daha sağlam altyapı:** Günlük dosyasında bellek sınırı, güvenli döndürme, API giriş doğrulaması ve açıklayıcı hatalar.

Ayrıntılar için [`YENILIKLER_v1.0.1.md`](YENILIKLER_v1.0.1.md) dosyasına bakın.

## ✨ Özellikler

| # | Özellik | # | Özellik |
|---|---|---|---|
| 1 | `.bat` ile tek tık başlatma | 14 | Uyarı sayacı |
| 2 | Python 3 kontrolü | 15 | Sunucu bağlantı durumu |
| 3 | Uygun portu otomatik bulma (8000–8010) | 16 | Kalıcı JSONL günlükler |
| 4 | Tarayıcıyı otomatik açma | 17 | Günlüklerde arama |
| 5 | Özel SQL Crack logosu | 18 | Olay seviyesi filtresi |
| 6 | Neon hacker tasarımı | 19 | Tarih filtresi |
| 7 | Mobil uyumlu arayüz | 20 | Günlük sayfalama |
| 8 | `v1.0.1` sürüm etiketi | 21 | JSON rapor indirme |
| 9 | 4 sahte demo hedefi | 22 | CSV rapor indirme |
| 10 | 6 simülasyon senaryosu | 23 | Sahte SQL dump üretme ve kaydetme |
| 11 | Yerel metin sınıflandırması | 24 | Dump listeleme, indirme ve silme |
| 12 | Canlı terminal ekranı | 25 | Günlük temizleme, kısayollar ve aktivite grafiği |
| 13 | Toplam olay sayacı | | |

## 🖥️ Kurulum ve çalıştırma

**Gereksinimler:** Windows ve **Python 3.9 veya üzeri**. Ek Python paketi gerekmez.

1. Projeyi indirip ZIP arşivinden **tamamen çıkar**. Klasör adı **`SQL Crack v1.0.1`** olur.
2. **`Start.py`** dosyasını `py -3 Start.py` ile çalıştır veya `SQL Crack Start.bat` dosyasına çift tıkla; BAT da `Start.py` çalıştırır.
3. Açılan CMD penceresini açık bırak. Tarayıcı otomatik açılır.
4. Tarayıcı açılmazsa CMD penceresinde yazan `127.0.0.1` adresini aç (genellikle `http://127.0.0.1:8000`).
5. Sunucuyu kapatmak için CMD üzerinde **Ctrl+C** kullan.

> Python bulunamıyorsa [Python'un resmî sitesinden](https://www.python.org/downloads/) Python 3 yükleyip kurulumda **Add Python to PATH** seçeneğini etkinleştir.

## 🧪 Nasıl kullanılır?

**Test Laboratuvarı** bölümünden bir sahte hedef ve simülasyon senaryosu seç. Testi çalıştırdıktan sonra sonuçları canlı terminalde ve olay günlüklerinde görüntüleyebilirsin. Arama, filtreleme ve rapor dışa aktarma özellikleriyle önceki sonuçları inceleyebilirsin.

**Sahte SQL dump** senaryosunu seçtiğinde uygulama eğitim için örnek `.sql` dosyası üretir. Bu dosyalar uygulamanın `data/dumps/` klasörüne kaydedilir; arayüz üzerinden görüntülenebilir, indirilebilir veya silinebilir.

## 📁 Proje yapısı

```text
SQL Crack v1.0.1/
├── Start.py                # Matrix / yazma animasyonu + baslatma
├── SQL Crack Start.bat
├── server.py
├── index.html
├── style.css
├── app.js
├── assets/
│   └── sql-crack-logo.png
└── data/
    ├── events.jsonl
    └── dumps/
```

| Dosya / klasör | Açıklama |
|---|---|
| `Start.py` | Havalı animasyon ve sunucuyu başlatma |
| `SQL Crack Start.bat` | Windows için Start.py başlatma kısayolu |
| `server.py` | Yerel web sunucusu ve demo API |
| `index.html`, `style.css`, `app.js` | Web arayüzü |
| `assets/` | Uygulama logosu |
| `data/events.jsonl` | Kalıcı simülasyon olay kayıtları |
| `data/dumps/` | Sentetik SQL örnekleri |

## 🔒 Güvenlik ve gizlilik

- Sunucu yalnızca **`127.0.0.1`** adresine bağlanır; dış ağ erişimine açılmaz.
- Gerçek SQL sorguları ve SQL enjeksiyon saldırıları çalıştırılmaz.
- Dump dosyaları gerçek sistemlerden alınan veriler değil, **örnek eğitim verileridir**.
- Teste girilen özel metnin içeriği kaydedilmez; yalnızca uzunluğu işlenir.
- Çalışma kayıtları bilgisayarındaki `data/` klasöründe saklanır.

## 🛠️ Sorun giderme

**CMD hemen kapanıyor:** Projeyi ZIP içinden değil, çıkardığın klasörden çalıştır. `server.py` ile `.bat` dosyasının aynı klasörde olduğundan emin ol.

**Python bulunamadı:** Komut İstemi'nde `py -3 --version` veya `python --version` komutunu dene.

**Tarayıcı açılmıyor:** CMD ekranında gösterilen adresi elle aç. `8000` doluysa sunucu `8001`–`8010` aralığından uygun bir port kullanabilir.

**Loglar kaydedilmiyor:** Proje klasöründe yazma iznin olduğundan emin ol.

## 👨‍💻 Yapımcı

**TarikPro43391**  
**Sürüm:** `v1.0.1`

---

<p align="center">💜 <strong>SQL Crack</strong> — Eğitim ve arayüz simülasyonu için geliştirilmiştir.</p>

## 🎬 Açılış animasyonu

`Start.py` başlatıldığında CMD içinde önce Matrix karakterleri akar; ardından ASCII SQL CRACK başlığı ve komut benzeri **tamamen sahte** durum satırları **harf harf** belirir. Açılış animasyonunun bitmesinin ardından yerel web paneli açılır.

- `py -3 Start.py --fast` — animasyon gecikmelerini atlar.
- `py -3 Start.py --no-animation` — Matrix efekti olmadan başlar.
- `py -3 Start.py --intro-only` — sadece tanıtımı oynatır.

Windows terminali ANSI renklerini desteklemiyorsa yazı temelli animasyon kullanılır. Bu ekran gerçek güvenlik kontrolleri yapıldığı anlamına gelmez.
