# 💜 SQL Crack v1.0.5 (Beta)

![SQL Crack logosu](assets/sql-crack-logo.png)

**SQL Crack**, Matrix tarzı CMD açılışı ve neon web arayüzü bulunan, eğitim ve izinli bağlantı kontrolleri için geliştirilmiş bir güvenlik laboratuvarıdır.

**Sürüm:** `v1.0.5 (Beta)`  
**Geliştirici:** `TarikPro43391`  
**Platform:** Windows, Python 3.9+

> **Önemli:** SQL enjeksiyonu, WAF atlatma, veri sızdırma veya gerçek veritabanından SQL dump alma işlemi yapılmaz. SQL senaryoları simülasyondur. HTTP kontrolleri yalnızca izin listesine eklenen adreslerde, sınırlı ve zararsız GET istekleriyle çalışır.

## 🚀 Kurulum ve çalıştırma

1. Projeyi ZIP olarak indir ve **tamamen çıkart**.
2. `SQL Crack v1.0.5 (Beta)` klasörüne gir.
3. `SQL Crack Start.bat` dosyasına çift tıkla.
4. `Start.py` Matrix animasyonunu ve harf harf yazılan terminal mesajlarını gösterir.
5. Sunucu başladığında web paneli tarayıcıda açılır. Açılmazsa CMD'de gösterilen adresi ziyaret et (genellikle `http://127.0.0.1:8000`).

Sunucuyu durdurmak için CMD'de **Ctrl+C** kullan. Python 3.9 veya üzeri yüklü olmalı; başka Python paketi gerekmiyor. Python'u [resmî sitesinden](https://www.python.org/downloads/) indirebilirsin.

**CMD ile alternatif başlatma:**

```bat
py -3 Start.py
```

| Komut | Ne yapar? |
|---|---|
| `py -3 Start.py` | Matrix intro ve web panelini başlatır |
| `py -3 Start.py --fast` | Intro beklemelerini atlar |
| `py -3 Start.py --no-animation` | Animasyonu kapatır |
| `py -3 Start.py --intro-only` | Yalnızca introyu gösterir |

## ✨ 32 özellik

| # | Özellik | # | Özellik |
|---|---|---|---|
| 1 | `.bat` ile tek tık başlatma | 17 | Loglarda arama |
| 2 | Python sürümü kontrolü | 18 | Olay seviyesi filtresi |
| 3 | Otomatik port seçimi | 19 | Tarih filtresi |
| 4 | Tarayıcıyı otomatik açma | 20 | Log sayfalama |
| 5 | Özel uygulama logosu | 21 | JSON raporu indirme |
| 6 | Neon hacker arayüzü | 22 | CSV raporu indirme |
| 7 | Mobil uyumlu tasarım | 23 | Sahte SQL dump üretme |
| 8 | `v1.0.5 (Beta)` etiketi | 24 | Dump indirme ve silme |
| 9 | Dört demo hedefi | 25 | Log temizleme ve aktivite grafiği |
| 10 | Altı test simülasyonu | 26 | İzinli HTTP GET kontrolü |
| 11 | Yerel metin analizi | 27 | Rastgele zararsız parametreler |
| 12 | Canlı terminal | 28 | Tam URL izin listesi |
| 13 | Toplam olay sayacı | 29 | İstek ve hız sınırı |
| 14 | Uyarı sayacı | 30 | Sunucu sağlık monitörü |
| 15 | Sunucu durum göstergesi | 31 | 24 saatlik karşılaştırmalı rapor |
| 16 | Kalıcı JSONL logları | 32 | Akıllı güvenlik/kota uyarıları |

## 🧪 Test laboratuvarı

Web panelinden demo hedefi ve simülasyon senaryosu seçip **Testi Başlat** düğmesini kullan. Sonuçlar canlı terminalde ve olay günlüğünde görünür. Günlükleri arayabilir, filtreleyebilir ve JSON/CSV biçiminde indirebilirsin.

### 🛡️ İzinli HTTP kontrolü

Gerçek HTTP kontrolleri yalnızca sahip olduğun veya açıkça test iznin bulunan adreslerde kullanılmalıdır. Harici HTTPS adreslerini `scope.json` içindeki `approved_urls` listesine tam URL olarak ekle.

```json
{
  "approved_urls": [
    "https://kendi-test-ortamin.example/health"
  ]
}
```

Bu örnek adres gerçek bir hedef değildir. Uygulama normalde kendi `/api/health` uç noktasını kullanabilir. Kontroller çalıştırma başına en fazla **3**, dakikada en fazla **6** istekle sınırlandırılır; istekler arasında en az **0,8 saniye** bulunur. Yanıt gövdeleri kaydedilmez ve yönlendirmeler izlenmez.

### 💾 Loglar ve örnek SQL dump

| Konum | İçerik |
|---|---|
| `data/events.jsonl` | Simülasyon ve kontrol günlükleri |
| `data/dumps/` | Yalnızca sentetik veri içeren örnek `.sql` dosyaları |

Örnek SQL dump özelliği **gerçek veritabanından veri çekmez**. Test kayıtlarını bilgisayarında tutar, gerekirse arayüz üzerinden indirebilirsin.

## 📊 İzleme

**Sunucu Sağlık Monitörü** çalışma süresi, yanıt sayısı, ortalama gecikme ve sunucu hatalarını gösterir. **Karşılaştırmalı Raporlar** son 24 saat ile önceki 24 saati karşılaştırır. **Akıllı Güvenlik** paneli reddedilen hedefleri, kalan istek kotasını ve bağlantı uyarılarını izler.

## 📁 Proje yapısı

```text
SQL Crack v1.0.5 (Beta)/
├── SQL Crack Start.bat
├── Start.py
├── server.py
├── safe_probes.py
├── insights.py
├── scope.json
├── index.html
├── style.css
├── app.js
├── assets/
│   └── sql-crack-logo.png
├── data/
│   ├── events.jsonl
│   └── dumps/
└── tests/
```

## 🛠️ Sorun giderme

- **CMD hemen kapanıyor:** ZIP dosyasını tamamen çıkardığından ve `.bat`, `Start.py`, `server.py` dosyalarının aynı klasörde olduğundan emin ol.
- **Python bulunamadı:** CMD'de `py -3 --version` komutunu çalıştır. Python 3.9+ kurulu ve PATH'e ekli olmalı.
- **Panel açılmıyor:** CMD açık kalmalı. Pencerede gösterilen yerel adresi tarayıcıda aç. 8000 portu doluysa 8001–8010 aralığı denenebilir.
- **Log kaydedilmiyor:** Proje klasörüne yazma iznini kontrol et.
- **HTTP testi reddedildi:** `scope.json` dosyasında tam hedef URL'nin izinli olduğundan emin ol.

## ✅ Testler

```bat
py -3 -m unittest discover -s tests -v
```

Otomatik testlerin geçmesi, Windows CMD animasyonunun her sistemde aynı görüntüleneceğini garanti etmez.

## 🆕 v1.0.5 (Beta) yenilikleri

- Matrix tarzı animasyonlu giriş ve harf harf yazılan terminal mesajları.
- İzinli hedeflere düşük hızda HTTP bağlantı kontrolleri.
- Zararsız rastgele parametreler ve kapsam doğrulaması.
- Günlük okuma/yazma dayanıklılığı iyileştirmeleri.
- Sunucu sağlığı, gelişmiş raporlar ve güvenlik uyarıları.
- Kod, belgeler ve klasör adlarında `v1.0.5 (Beta)` etiketi.

---

**Yapımcı:** TarikPro43391  
**Sürüm:** `v1.0.5 (Beta)`  
**Amaç:** Eğitim, simülasyon ve izinli bağlantı testi.
