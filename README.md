<div align="center">

<img src="assets/sql-crack-logo.png" alt="SQL Crack logosu" width="170" />

# 💚 SQL Crack v1.0.1

### MATRIX EDITION · SQL GÜVENLİK TEST SİMÜLATÖRÜ

**Neon hacker arayüzü • Sinematik CMD açılışı • Canlı terminal • Kalıcı loglar • Demo SQL dump**

**Yapımcı:** `TarikPro43391`  ·  **Sürüm:** `v1.0.1`

</div>

---

> [!IMPORTANT]
> **SQL Crack eğitim amaçlı bir simülasyon uygulamasıdır.** Gerçek web sitelerine SQL enjeksiyonu yapmaz, WAF veya güvenlik duvarı aşmaz, gerçek veritabanlarına bağlanmaz ve bilgi sızdırmaz. Açılıştaki havalı komutlar ve erişim mesajları yalnızca görsel efekttir. SQL dump dosyaları tamamen **sahte örnek verilerden** üretilir.

## 🎬 Yeni Matrix açılışı

`SQL Crack Start.bat` dosyasına çift tıkladığında `Start.py` çalışır ve CMD ekranında sırasıyla:

1. **Matrix yağmuru:** Yeşil karakterler terminal ekranında akar.
2. **ASCII SQL CRACK logosu:** Başlık terminalde belirir.
3. **Harf harf yazılan komutlar:** Açılış satırları tek seferde değil, yazılıyormuş gibi görünür.
4. **Aşamalı `[OK]` mesajları:** Simüle edilen hazırlık adımları gösterilir.
5. **Web paneli:** Intro tamamlandığında yerel arayüz açılır.

```text
  ____   ___  _        ____ ____      _    ____ _  __
 / ___| / _ \| |      / ___|  _ \    / \  / ___| |/ /
 \___ \| | | | |     | |   | |_) |  / _ \| |   | ' /
  ___) | |_| | |___  | |___|  _ <  / ___ \ |___| . \
 |____/ \__\_\_____|  \____|_| \_\/_/   \_\____|_|\_\

[+] DEVELOPER / CREATOR : tarikpro43391
[+] ENGINE VERSION      : v1.0.1 [STABLE-BUILD]
[+] TARGET DATABASE     : [SIMULATION / NO CONNECTION]
[+] ACCESS CLEARANCE    : DEMO_MODE // LOCAL_ONLY

C:\SQL_CRACK> boot --module=sql-crack --profile=simulation
     [OK] Simulated sequence completed.

[>>>] ACCESS GRANTED (DEMO). STARTING LOCAL WEB PANEL...
```

*Terminal çıktısı temsili bir ön izlemedir. Gerçek açılışta yazı animasyonu ve Matrix efekti kullanılır.*

## ✨ 25 temel özellik

| # | Özellik | # | Özellik |
|---|---|---|---|
| 01 | `.bat` ile kolay başlatma | 14 | Uyarı sayacı |
| 02 | Python sürüm denetimi | 15 | Sunucu durumu göstergesi |
| 03 | Uygun portu seçme (`8000–8010`) | 16 | Kalıcı JSONL log dosyası |
| 04 | Tarayıcıyı otomatik açma | 17 | Loglarda arama |
| 05 | SQL Crack uygulama logosu | 18 | Seviye filtresi |
| 06 | Neon siberpunk tasarım | 19 | Tarih filtresi |
| 07 | Mobil uyumlu web paneli | 20 | Sayfalama |
| 08 | `v1.0.1` sürüm bilgisi | 21 | JSON raporu indirme |
| 09 | 4 sahte test hedefi | 22 | CSV raporu indirme |
| 10 | 6 eğitim senaryosu | 23 | Sahte SQL dump oluşturma |
| 11 | Yerel test metni sınıflandırması | 24 | Dump listeleme, indirme, silme |
| 12 | Canlı terminal konsolu | 25 | Log temizleme, kısayollar ve etkinlik grafiği |
| 13 | Toplam olay sayacı | | |

### 🆕 v1.0.1 ile gelenler

- 💚 **Matrix tarzı CMD introsu:** Akan karakterler ve yazma animasyonu.
- 🖥️ **Yeni başlatıcı:** `SQL Crack Start.bat` → `Start.py`.
- 🔁 **Son Testi Tekrarla:** Önceki eğitim simülasyonunu yeniden çalıştır.
- 📄 **Terminali TXT olarak indir:** Konsol çıktılarını metin dosyası şeklinde kaydet.
- ⏯️ **Otomatik yenileme kontrolü:** Günlük yenilemeyi durdur veya sürdür.
- 🛠️ **Hata iyileştirmeleri:** Eksik dosya, Python sürümü, giriş doğrulama ve günlük dosyası büyümesi için ek kontroller.

Ayrıntılar: [`YENILIKLER_v1.0.1.md`](YENILIKLER_v1.0.1.md)

## 🚀 Kurulum

**Gereksinimler:** Windows 10/11, **Python 3.9 veya üzeri** ve güncel bir web tarayıcısı. Ek Python paketi kurman gerekmez.

1. Projenin ZIP dosyasını indir.
2. ZIP'i **tamamen dışarı çıkar**.
3. `SQL Crack v1.0.1` klasörünü aç.
4. **`SQL Crack Start.bat`** dosyasına çift tıkla.
5. Matrix introsu tamamlanınca tarayıcının açılmasını bekle.

Sunucu yalnızca bu bilgisayarda çalışır. Tarayıcı otomatik açılmazsa CMD penceresinde gösterilen adresi aç; varsayılan adres `http://127.0.0.1:8000` şeklindedir. Bu port doluysa program uygun başka bir port kullanabilir.

> [!TIP]
> Python yüklü değilse [python.org](https://www.python.org/downloads/) üzerinden kurabilirsin. Windows kurulumunda **Add Python to PATH** seçeneğini etkinleştir.

### ⌨️ Start.py ile çalıştırma

Proje klasöründe CMD açıp aşağıdaki komutları kullanabilirsin:

```bat
py -3 Start.py
```

| Komut | İşlev |
|---|---|
| `py -3 Start.py` | Normal Matrix animasyonu ile başlatır |
| `py -3 Start.py --fast` | Animasyon gecikmelerini atlayarak açar |
| `py -3 Start.py --no-animation` | Matrix efekti olmadan başlatır |
| `py -3 Start.py --intro-only` | Yalnızca intro gösterir; web sunucusunu açmaz |

Uygulamayı kapatmak için CMD penceresinde **Ctrl+C** tuşlarına bas.

## 🧪 Kullanım

1. Web panelinde bir **demo hedefi** ve **simülasyon senaryosu** seç.
2. Simülasyonu başlat.
3. Sonucu terminal ekranında ve olay günlüğünde incele.
4. Kayıtları ara, filtrele veya JSON/CSV olarak dışarı aktar.
5. **Sahte SQL dump** senaryosuyla yalnızca eğitim verisi içeren `.sql` dosyası oluştur.

### 💾 Kayıtlar nereye gidiyor?

- **Olay kayıtları:** `data/events.jsonl`
- **Sahte SQL dump dosyaları:** `data/dumps/`
- **Raporlar:** Tarayıcının varsayılan indirme klasörü (JSON / CSV)
- **Terminal TXT:** İndirme işlemi yapıldığında tarayıcının indirme klasörü

`data/` klasörünü korursan önceki eğitim kayıtlarını da saklayabilirsin. Kayıtları paylaşmadan önce içeriğini kontrol et.

## 📁 Dosya yapısı

```text
SQL Crack v1.0.1/
├── SQL Crack Start.bat       # Windows başlatıcısı
├── Start.py                  # Matrix intro ve yazma efekti
├── server.py                 # Yerel demo sunucusu ve API
├── index.html                # Web panelinin yapısı
├── style.css                 # Neon tema
├── app.js                    # Arayüz davranışları
├── assets/
│   └── sql-crack-logo.png    # Uygulama logosu
├── data/
│   ├── events.jsonl          # Eğitim olay günlükleri
│   └── dumps/                # Sentetik SQL dosyaları
├── tests/                    # Otomatik testler
├── YENILIKLER_v1.0.1.md     # Sürüm notları
└── README.md                 # Bu dosya
```

## 🛡️ Güvenlik

- Yerel web sunucusu `127.0.0.1` adresine bağlanır.
- Test hedefleri **gerçek sistem değil**, uygulama içinde tanımlanmış sahte senaryolardır.
- SQL enjeksiyonu, WAF atlatma, veri çekme veya yetkisiz erişim **gerçekleştirilmez**.
- Üretilen `.sql` dosyaları sentetik örnek kayıtlar içerir.
- Özel test metinlerinin içeriği günlük dosyasına yazılmaz; yalnızca uzunluğu işlenir.

## 🛠️ Sorun giderme

**`SQL Crack Start.bat` açılmıyor:** ZIP arşivini tamamen çıkar. `.bat`, `Start.py` ve `server.py` aynı klasörde olmalı.

**`Python 3.9+ bulunamadı` hatası:** CMD'de `py -3 --version` komutunu çalıştır. Python kurulumunu ve PATH ayarını kontrol et.

**Matrix efekti görünmüyor:** Terminalin ANSI renk desteği sınırlı olabilir. Animasyonun metin tabanlı yedek görünümü kullanılabilir. Windows Terminal veya güncel CMD kullan.

**Web paneli açılmıyor:** CMD'de gösterilen `127.0.0.1` adresini tarayıcıya yaz. Sunucunun çalıştığı pencere açık kalmalı.

**Loglar kaydedilmiyor:** Proje klasörüne yazma iznin olduğundan emin ol; `data/` klasörünü kontrol et.

**Yalnızca intro izlemek istiyorum:** `py -3 Start.py --intro-only` komutunu çalıştır.

---

<div align="center">

**SQL Crack · v1.0.1**

**Geliştirici: TarikPro43391**

*CODE WRITTEN IN THE DARK. POWER UNLOCKED BY tarikpro43391.*

💚 **Eğitim, simülasyon ve arayüz deneyimi için hazırlanmıştır.**

</div>
