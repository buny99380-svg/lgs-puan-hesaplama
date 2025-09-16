# 🚀 LGS Puan Hesaplama - Render Deployment Rehberi

## 📋 Ön Hazırlık

### 1. GitHub Repository Oluşturma
```bash
git init
git add .
git commit -m "Initial commit - LGS Puan Hesaplama System"
git branch -M main
git remote add origin https://github.com/yourusername/lgs-puan-hesaplama.git
git push -u origin main
```

### 2. Gerekli Dosyalar Kontrolü
✅ `render.yaml` - Render konfigürasyonu
✅ `requirements.txt` - Python bağımlılıkları
✅ `app.py` - Ana uygulama (PostgreSQL desteği ile)
✅ `robots.txt` - SEO için
✅ Sitemap endpoint - `/sitemap.xml`

## 🌐 Render'da Deployment

### Adım 1: Render Hesabı
1. [render.com](https://render.com) adresine gidin
2. GitHub hesabınızla giriş yapın
3. "New +" butonuna tıklayın

### Adım 2: Web Service Oluşturma
1. "Web Service" seçin
2. GitHub repository'nizi seçin
3. Aşağıdaki ayarları yapın:

**Temel Ayarlar:**
- **Name:** `lgs-puan-hesaplama`
- **Region:** `Frankfurt (EU Central)`
- **Branch:** `main`
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`

### Adım 3: Environment Variables
Aşağıdaki environment variable'ları ekleyin:

```
SECRET_KEY = [Auto-generate]
OPENROUTER_API_KEY = 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
```

### Adım 4: PostgreSQL Database
1. "New +" → "PostgreSQL" seçin
2. **Database Name:** `lgs-database`
3. **Database User:** `lgs_user`
4. **Region:** `Frankfurt (EU Central)`
5. Database oluştuktan sonra, Web Service'e DATABASE_URL'i otomatik bağlayın

### Adım 5: Deploy
1. "Create Web Service" butonuna tıklayın
2. Deploy işleminin tamamlanmasını bekleyin (5-10 dakika)
3. Yeşil "Live" durumunu görene kadar bekleyin

## 🔍 Google Search Console Kurulumu

### Adım 1: Domain Doğrulama
1. [Google Search Console](https://search.google.com/search-console/) adresine gidin
2. "Add Property" → "URL prefix" seçin
3. Render URL'inizi girin: `https://your-app-name.onrender.com`

### Adım 2: HTML Tag Doğrulaması
1. Google'dan aldığınız meta tag'i `base.html` dosyasına ekleyin:
```html
<meta name="google-site-verification" content="your-verification-code" />
```

### Adım 3: Sitemap Gönderimi
1. Search Console'da "Sitemaps" bölümüne gidin
2. Sitemap URL'ini ekleyin: `https://your-app-name.onrender.com/sitemap.xml`
3. "Submit" butonuna tıklayın

### Adım 4: URL Inspection
1. Ana sayfanızı test edin: `https://your-app-name.onrender.com`
2. "Request Indexing" butonuna tıklayın
3. Diğer önemli sayfalar için de tekrarlayın

## 📊 SEO Optimizasyonu Kontrolleri

### ✅ Teknik SEO
- [x] Meta title ve description
- [x] Open Graph tags
- [x] Twitter Card tags
- [x] Structured data (JSON-LD)
- [x] Canonical URLs
- [x] Robots.txt
- [x] XML Sitemap
- [x] Mobile responsive
- [x] HTTPS (Render otomatik sağlar)

### ✅ İçerik SEO
- [x] H1, H2, H3 tag yapısı
- [x] Alt text'ler (aria-hidden ile)
- [x] Semantic HTML5 elements
- [x] Internal linking
- [x] Türkçe keyword optimization

## 🚨 Deployment Sonrası Kontroller

### 1. Fonksiyonellik Testi
- [ ] Kullanıcı kaydı/girişi
- [ ] Puan hesaplama
- [ ] Okul önerileri
- [ ] Deneme sınavı kayıtları
- [ ] AI önerileri
- [ ] Başarı rozetleri

### 2. SEO Testi
- [ ] robots.txt erişimi: `/robots.txt`
- [ ] Sitemap erişimi: `/sitemap.xml`
- [ ] Meta tag'lar görünüyor
- [ ] Structured data geçerli
- [ ] Mobile responsive

### 3. Performance Testi
- [ ] Sayfa yükleme hızı (<3 saniye)
- [ ] Database bağlantısı
- [ ] Static dosyalar yükleniyor
- [ ] HTTPS çalışıyor

## 🔧 Troubleshooting

### Database Bağlantı Hatası
```bash
# Render logs kontrol edin
# Environment variables doğru mu kontrol edin
# PostgreSQL database aktif mi kontrol edin
```

### Static Files Yüklenmiyor
```python
# app.py dosyasında static files route'u kontrol edin
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)
```

### SSL/HTTPS Hatası
- Render otomatik SSL sertifikası sağlar
- Custom domain kullanıyorsanız DNS ayarlarını kontrol edin

## 📈 Monitoring

### Render Dashboard
- CPU/Memory kullanımı
- Response time
- Error logs
- Deploy history

### Google Analytics (Opsiyonel)
```html
<!-- Google Analytics tag'ini base.html'e ekleyin -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

## 🎯 Production URL
Deployment tamamlandıktan sonra siteniz şu adreste yayında olacak:
`https://your-app-name.onrender.com`

## 📞 Destek
Herhangi bir sorun yaşarsanız:
1. Render logs'ları kontrol edin
2. GitHub issues oluşturun
3. Google Search Console'da hata raporlarını kontrol edin
