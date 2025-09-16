# LGS Puan Hesaplama Sistemi

AI destekli modern LGS (Liselere Giriş Sistemi) puan hesaplama ve çalışma takip sistemi.

## 🚀 Özellikler

### ✨ Temel Özellikler
- **Doğru LGS Puan Hesaplama**: Resmi katsayılarla tam doğru hesaplama
- **Kullanıcı Hesap Sistemi**: Güvenli kayıt ve giriş sistemi
- **Puan Geçmişi**: Tüm hesaplamalarınızı takip edin
- **Yüzdelik Dilim**: Performansınızı diğer öğrencilerle karşılaştırın

### 🤖 AI Destekli Özellikler
- **Kişiselleştirilmiş Çalışma Planı**: AI ile özel çalışma programı
- **Gelişim Önerileri**: Zayıf alanlarınız için spesifik tavsiyeler
- **Motivasyon Mesajları**: AI destekli motivasyonel içerik
- **Akıllı Analiz**: Performans trendlerinizi analiz edin

### 📊 Analitik ve Raporlama
- **Grafik Analizi**: Puan gelişim grafikleri
- **Ders Bazında Performans**: Radar grafik ile detaylı analiz
- **İstatistikler**: Ortalama, en yüksek puan ve gelişim oranları
- **Rapor İndirme**: Detaylı PDF raporları

### 🎨 Modern Arayüz
- **Responsive Tasarım**: Mobil ve masaüstü uyumlu
- **Animasyonlar**: Smooth geçişler ve görsel efektler
- **Dark/Light Mode**: Göz dostu arayüz seçenekleri
- **Kullanıcı Dostu**: Sezgisel ve kolay kullanım

## 🛠️ Kurulum

### Gereksinimler
- Python 3.8+
- pip (Python paket yöneticisi)

### Adım Adım Kurulum

1. **Projeyi İndirin**
```bash
git clone <repository-url>
cd lgspuanhesaplama
```

2. **Sanal Ortam Oluşturun (Önerilen)**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Gerekli Paketleri Yükleyin**
```bash
pip install -r requirements.txt
```

4. **Uygulamayı Başlatın**
```bash
python app.py
```

5. **Tarayıcınızda Açın**
```
http://localhost:5000
```

## 🔧 Yapılandırma

### Ortam Değişkenleri
`.env` dosyası oluşturup aşağıdaki değişkenleri ekleyin:

```env
SECRET_KEY=your-secret-key-here
OPENROUTER_API_KEY=your-openrouter-api-key
DATABASE_URL=sqlite:///lgs_database.db
```

### AI API Anahtarı
OpenRouter AI özelliklerini kullanmak için:
1. [OpenRouter](https://openrouter.ai) hesabı oluşturun
2. API anahtarınızı alın
3. `app.py` dosyasındaki `OPENROUTER_API_KEY` değişkenini güncelleyin

## 📖 Kullanım Kılavuzu

### İlk Kullanım
1. **Kayıt Olun**: Ana sayfada "Kayıt Ol" butonuna tıklayın
2. **Giriş Yapın**: Kullanıcı adı ve şifrenizle giriş yapın
3. **Puan Hesaplayın**: Dashboard'da doğru/yanlış sayılarınızı girin
4. **AI Önerilerini Alın**: AI sekmesinden kişiselleştirilmiş öneriler alın

### Puan Hesaplama
- Her ders için doğru ve yanlış sayılarını girin
- Sistem otomatik olarak net hesaplaması yapar (3 yanlış = 1 doğru)
- Resmi LGS katsayıları kullanılarak puan hesaplanır
- Sonuçlar otomatik olarak kaydedilir

### AI Önerileri
- **Çalışma Planı**: Haftalık çalışma programı
- **Gelişim Önerileri**: Zayıf dersler için spesifik tavsiyeler
- **Motivasyon**: Kişiselleştirilmiş motivasyon mesajları

## 🏗️ Teknik Detaylar

### Teknoloji Stack
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI**: OpenRouter API (Claude 3 Haiku)
- **Charts**: Chart.js
- **Icons**: Font Awesome

### Veritabanı Yapısı
- **Users**: Kullanıcı bilgileri
- **Scores**: Puan hesaplamaları
- **StudySessions**: Çalışma seansları
- **AIRecommendations**: AI önerileri

### API Endpoints
- `POST /register` - Kullanıcı kaydı
- `POST /login` - Kullanıcı girişi
- `POST /calculate` - Puan hesaplama
- `GET /ai-recommendations` - AI önerileri
- `GET /analytics` - Analitik veriler

## 🔒 Güvenlik

- Şifreler hash'lenerek saklanır
- Session tabanlı kimlik doğrulama
- CSRF koruması
- Input validasyonu
- SQL injection koruması

## 🚀 Deployment

### Heroku Deployment
```bash
# Heroku CLI kurulu olmalı
heroku create your-app-name
git push heroku main
heroku config:set OPENROUTER_API_KEY=your-key
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 👨‍💻 Geliştirici

**Bunyamin Palta**
- GitHub: [@bunyaminpalta]
- Email: [your-email@example.com]

## 🆘 Destek

Herhangi bir sorun yaşarsanız:
1. GitHub Issues kullanın
2. Email ile iletişime geçin
3. Dokümantasyonu kontrol edin

## 📊 LGS Puan Hesaplama Formülü

```
Net = Doğru - (Yanlış / 3)
Ağırlıklı Puan = Net × Katsayı
Toplam Puan = 194.65 + Σ(Ağırlıklı Puanlar)
```

### Katsayılar
- Türkçe: 4.35
- Matematik: 4.26
- Fen Bilimleri: 4.13
- T.C. İnkılap Tarihi: 1.67
- Din Kültürü: 1.90
- İngilizce: 1.51

## 🎯 Gelecek Özellikler

- [ ] Mobil uygulama
- [ ] Çoklu dil desteği
- [ ] Sosyal özellikler
- [ ] Gelişmiş AI modelleri
- [ ] Öğretmen paneli
- [ ] Bulk import/export
- [ ] API dokumentasyonu
- [ ] Unit testler

---

**Not**: Bu sistem eğitim amaçlıdır. Resmi LGS sonuçları için MEB'in açıkladığı sonuçları takip edin.
