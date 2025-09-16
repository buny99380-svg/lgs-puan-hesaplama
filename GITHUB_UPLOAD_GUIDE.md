# 📚 GitHub'a Yükleme - Detaylı Rehber

## 🔧 Ön Hazırlık

### 1. Git Kurulumu Kontrolü
Önce Git'in bilgisayarınızda kurulu olup olmadığını kontrol edin:

```bash
git --version
```

Eğer Git kurulu değilse:
- [git-scm.com](https://git-scm.com/download/win) adresinden indirin
- Kurulum sırasında tüm varsayılan ayarları kabul edin

### 2. Git Konfigürasyonu (İlk Kez Yapılacak)
```bash
git config --global user.name "Adınız Soyadınız"
git config --global user.email "email@example.com"
```

## 🌐 GitHub Repository Oluşturma

### Adım 1: GitHub'da Yeni Repository
1. [github.com](https://github.com) adresine gidin
2. Sağ üst köşedeki **"+"** işaretine tıklayın
3. **"New repository"** seçin
4. Repository ayarları:
   - **Repository name:** `lgs-puan-hesaplama`
   - **Description:** `LGS Puan Hesaplama ve Okul Önerisi Sistemi`
   - **Public** seçin (ücretsiz hosting için)
   - **Add a README file** - ✅ İŞARETLEMEYİN
   - **Add .gitignore** - ✅ İŞARETLEMEYİN
   - **Choose a license** - ✅ İŞARETLEMEYİN
5. **"Create repository"** butonuna tıklayın

### Adım 2: Repository URL'ini Kopyalayın
Repository oluştuktan sonra, yeşil **"Code"** butonuna tıklayın ve HTTPS URL'ini kopyalayın:
```
https://github.com/yourusername/lgs-puan-hesaplama.git
```

## 💻 Terminal/Command Prompt İşlemleri

### Adım 1: Proje Klasörüne Gidin
```bash
cd C:\Users\bunya\Desktop\lgspuanhesaplama
```

### Adım 2: Git Repository Başlatın
```bash
git init
```
Bu komut klasörünüzü bir Git repository'sine dönüştürür.

### Adım 3: .gitignore Dosyası Oluşturun
```bash
echo. > .gitignore
```

Sonra .gitignore dosyasını açın ve şu içeriği ekleyin:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite
*.sqlite3

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

### Adım 4: Tüm Dosyaları Staging Area'ya Ekleyin
```bash
git add .
```
Bu komut tüm dosyaları Git'in takip etmesi için hazırlar.

### Adım 5: İlk Commit'i Yapın
```bash
git commit -m "Initial commit: LGS Puan Hesaplama Sistemi"
```

### Adım 6: Ana Branch'i Ayarlayın
```bash
git branch -M main
```

### Adım 7: Remote Repository Bağlayın
```bash
git remote add origin https://github.com/yourusername/lgs-puan-hesaplama.git
```
**NOT:** `yourusername` yerine kendi GitHub kullanıcı adınızı yazın!

### Adım 8: GitHub'a Yükleyin
```bash
git push -u origin main
```

İlk kez push yaparken GitHub kullanıcı adı ve şifrenizi (veya personal access token) isteyecek.

## 🔐 GitHub Authentication

### Personal Access Token Oluşturma (Önerilen)
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "Generate new token (classic)"
3. **Note:** `LGS Puan Hesaplama`
4. **Expiration:** `90 days` (veya istediğiniz süre)
5. **Scopes:** `repo` kutusunu işaretleyin
6. "Generate token" butonuna tıklayın
7. Token'ı kopyalayın ve güvenli bir yerde saklayın

### Token ile Push
```bash
git push -u origin main
```
- **Username:** GitHub kullanıcı adınız
- **Password:** Personal access token (şifre değil!)

## 📁 Dosya Yapısı Kontrolü

Yükleme öncesi dosya yapınız şöyle olmalı:
```
lgs-puan-hesaplama/
├── .gitignore
├── app.py
├── requirements.txt
├── render.yaml
├── DEPLOYMENT.md
├── GITHUB_UPLOAD_GUIDE.md
├── .env.example
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   └── dashboard.js
│   ├── images/
│   │   └── .gitkeep
│   └── robots.txt
├── templates/
│   ├── base.html
│   ├── login.html
│   └── dashboard.html
├── instance/
│   └── lgs_database.db (bu dosya .gitignore'da)
└── run.py
```

## 🔄 Güncellemeler İçin

Kod değişikliği yaptıktan sonra:

```bash
# Değişiklikleri kontrol edin
git status

# Değişiklikleri ekleyin
git add .

# Commit yapın
git commit -m "Açıklayıcı commit mesajı"

# GitHub'a gönderin
git push
```

## 🚨 Yaygın Hatalar ve Çözümleri

### Hata 1: "fatal: not a git repository"
**Çözüm:**
```bash
git init
```

### Hata 2: "remote origin already exists"
**Çözüm:**
```bash
git remote remove origin
git remote add origin https://github.com/yourusername/lgs-puan-hesaplama.git
```

### Hata 3: "Authentication failed"
**Çözüm:**
- Personal access token kullanın (şifre değil)
- Token'ın `repo` yetkisine sahip olduğundan emin olun

### Hata 4: "Updates were rejected"
**Çözüm:**
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

### Hata 5: Büyük dosya hatası
**Çözüm:**
```bash
# .gitignore'a ekleyin ve tekrar commit yapın
echo "*.db" >> .gitignore
git rm --cached instance/lgs_database.db
git commit -m "Remove database file"
git push
```

## ✅ Başarı Kontrolü

GitHub repository'nizde şunları görmelisiniz:
- Tüm proje dosyaları
- Yeşil "✓" commit işareti
- README.md (otomatik oluşacak)
- Son commit tarihi

## 🔗 Faydalı Komutlar

```bash
# Repository durumunu kontrol et
git status

# Commit geçmişini gör
git log --oneline

# Remote repository'leri listele
git remote -v

# Branch'leri listele
git branch

# Dosya değişikliklerini gör
git diff
```

## 📞 Yardım

Sorun yaşarsanız:
1. Hata mesajını tam olarak okuyun
2. Google'da "git [hata mesajı]" arayın
3. GitHub'ın kendi dokümantasyonunu kontrol edin
4. Stack Overflow'da arayın

Repository başarıyla oluşturulduktan sonra Render deployment'a geçebilirsiniz!
