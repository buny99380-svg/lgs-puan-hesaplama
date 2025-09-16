import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import requests
import json
from urllib.parse import urlparse
import sqlite3

app = Flask(__name__)

# Production configuration
if os.environ.get('DATABASE_URL'):
    # Production - PostgreSQL on Render
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Development - SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/lgs_database.db'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lgs-puan-hesaplama-secret-key-2024')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# OpenRouter API configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', "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")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='user', lazy=True, cascade='all, delete-orphan')
    study_sessions = db.relationship('StudySession', backref='user', lazy=True, cascade='all, delete-orphan')

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    turkce_dogru = db.Column(db.Integer, default=0)
    turkce_yanlis = db.Column(db.Integer, default=0)
    matematik_dogru = db.Column(db.Integer, default=0)
    matematik_yanlis = db.Column(db.Integer, default=0)
    fen_dogru = db.Column(db.Integer, default=0)
    fen_yanlis = db.Column(db.Integer, default=0)
    inkilap_dogru = db.Column(db.Integer, default=0)
    inkilap_yanlis = db.Column(db.Integer, default=0)
    din_dogru = db.Column(db.Integer, default=0)
    din_yanlis = db.Column(db.Integer, default=0)
    ingilizce_dogru = db.Column(db.Integer, default=0)
    ingilizce_yanlis = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Float, nullable=False)
    percentile = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    topics_studied = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recommendation_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    school_type = db.Column(db.String(50), nullable=False)
    min_score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    quota = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MockExam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_name = db.Column(db.String(100), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    wrong_answers = db.Column(db.Integer, nullable=False)
    empty_answers = db.Column(db.Integer, nullable=False)
    time_spent = db.Column(db.Integer, nullable=False)
    subject_scores = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    target_score = db.Column(db.Float, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    daily_study_hours = db.Column(db.Float, nullable=False)
    subjects_focus = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    badge_icon = db.Column(db.String(50), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper Functions
def calculate_score(data):
    """Calculate LGS score based on correct and wrong answers"""
    coefficients = {
        'turkce': 4.35,
        'matematik': 4.26,
        'fen': 4.13,
        'inkilap': 1.67,
        'din': 1.90,
        'ingilizce': 1.51
    }
    
    # Calculate nets (3 wrong answers cancel 1 correct answer)
    nets = {}
    for subject in coefficients.keys():
        dogru = data.get(f'{subject}_dogru', 0)
        yanlis = data.get(f'{subject}_yanlis', 0)
        nets[subject] = max(0, dogru - (yanlis / 3))
    
    # Calculate weighted score
    weighted_score = sum(nets[subject] * coefficients[subject] for subject in coefficients.keys())
    
    # Add constant and ensure score is within bounds
    total_score = max(100, min(500, 194.65 + weighted_score))
    
    # Calculate percentile (simplified normal distribution)
    mean, std_dev = 300, 50
    z_score = (total_score - mean) / std_dev
    percentile = max(0.01, min(99.99, 100 * (1 / (1 + pow(2.718, -1.702 * z_score)))))
    
    return {
        'total_score': round(total_score, 2),
        'percentile': round(percentile, 2),
        'nets': {k: round(v, 2) for k, v in nets.items()}
    }

def get_ai_recommendation(user_scores, recommendation_type="study_plan"):
    """Get AI-powered recommendations using OpenRouter API"""
    try:
        # Prepare user data for AI analysis
        latest_score = user_scores[-1] if user_scores else None
        if not latest_score:
            return "Henüz puan hesaplaması yapmadınız. Lütfen önce bir deneme sınavı sonucunuzu girin."
        
        # Create prompt based on user's performance
        weak_subjects = []
        strong_subjects = []
        
        subjects = ['turkce', 'matematik', 'fen', 'inkilap', 'din', 'ingilizce']
        max_questions = {'turkce': 20, 'matematik': 20, 'fen': 20, 'inkilap': 10, 'din': 10, 'ingilizce': 10}
        
        for subject in subjects:
            dogru = getattr(latest_score, f'{subject}_dogru', 0)
            max_q = max_questions[subject]
            success_rate = (dogru / max_q) * 100 if max_q > 0 else 0
            
            if success_rate < 60:
                weak_subjects.append(f"{subject.title()}: %{success_rate:.1f}")
            elif success_rate > 80:
                strong_subjects.append(f"{subject.title()}: %{success_rate:.1f}")
        
        if recommendation_type == "study_plan":
            prompt = f"""
            LGS öğrencisi için kişiselleştirilmiş çalışma planı oluştur.
            
            Öğrenci Bilgileri:
            - Toplam Puan: {latest_score.total_score}
            - Yüzdelik Dilim: %{latest_score.percentile}
            - Zayıf Dersler: {', '.join(weak_subjects) if weak_subjects else 'Yok'}
            - Güçlü Dersler: {', '.join(strong_subjects) if strong_subjects else 'Yok'}
            
            Lütfen:
            1. Haftalık çalışma programı öner
            2. Zayıf derslere odaklanma stratejileri ver
            3. Güçlü dersleri koruma önerileri sun
            4. Motivasyonel tavsiyeler ekle
            
            Türkçe olarak, pratik ve uygulanabilir öneriler ver.
            """
        elif recommendation_type == "improvement":
            prompt = f"""
            LGS öğrencisi için gelişim önerileri oluştur.
            
            Mevcut Durum:
            - Puan: {latest_score.total_score}/500
            - Yüzdelik: %{latest_score.percentile}
            - Gelişim Gereken Alanlar: {', '.join(weak_subjects)}
            
            Her zayıf ders için:
            1. Spesifik çalışma teknikleri
            2. Kaynak önerileri
            3. Pratik egzersizler
            4. Zaman yönetimi
            
            Kısa ve öz, Türkçe yanıt ver.
            """
        else:  # motivation
            prompt = f"""
            LGS öğrencisi için motivasyonel mesaj oluştur.
            
            Öğrenci Durumu:
            - Puan: {latest_score.total_score}
            - Başarı Oranı: %{latest_score.percentile}
            
            Pozitif, destekleyici ve motive edici bir mesaj yaz.
            Başarıları vurgula, gelişim alanlarını umut verici şekilde sun.
            Türkçe, samimi bir dille yaz.
            """
        
        # List of free models to try
        free_models = [
            'qwen/qwen-2.5-72b-instruct:free',
            'qwen/qwen-2.5-14b-instruct:free',
            'google/gemma-2-9b-it:free',
            'mistralai/mistral-7b-instruct:free',
            'meta-llama/llama-3.2-3b-instruct:free'
        ]
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "LGS Puan Hesaplama Sistemi"
        }
        
        # Try each model until one works
        for model in free_models:
            try:
                data = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                else:
                    print(f"Model {model} failed with status {response.status_code}")
                    continue
                    
            except Exception as model_error:
                print(f"Error with model {model}: {str(model_error)}")
                continue
        
        # If all models fail, return a fallback response
        return generate_fallback_recommendation(latest_score, recommendation_type, weak_subjects, strong_subjects)
            
    except Exception as e:
        return f"AI önerisi oluşturulurken hata oluştu: {str(e)}"

def generate_fallback_recommendation(latest_score, recommendation_type, weak_subjects, strong_subjects):
    """Generate fallback recommendations when AI API fails"""
    if recommendation_type == "study_plan":
        return f"""
        📚 Kişiselleştirilmiş Çalışma Planı
        
        Mevcut Puanınız: {latest_score.total_score:.1f}/500 (%{latest_score.percentile:.1f} dilim)
        
        🎯 Haftalık Program:
        • Pazartesi-Çarşamba: Zayıf dersler ({', '.join([s.split(':')[0] for s in weak_subjects]) if weak_subjects else 'Tüm dersler'})
        • Perşembe-Cuma: Güçlü dersleri pekiştirme
        • Hafta sonu: Deneme sınavları ve tekrar
        
        📈 Strateji:
        • Günde 3-4 saat odaklanmış çalışma
        • Her ders için 45 dk çalışma, 15 dk mola
        • Zayıf derslere %60 zaman ayırın
        
        💪 Motivasyon: Her küçük ilerleme büyük başarının parçasıdır!
        """
    elif recommendation_type == "improvement":
        return f"""
        🚀 Gelişim Önerileri
        
        Odaklanmanız Gereken Alanlar:
        {chr(10).join([f'• {subject}' for subject in weak_subjects]) if weak_subjects else '• Tüm derslerde dengeli gelişim'}
        
        📖 Çalışma Teknikleri:
        • Aktif okuma ve not alma
        • Konu özetleri çıkarma
        • Düzenli tekrar yapma
        • Soru çözme pratiği
        
        ⏰ Zaman Yönetimi:
        • Pomodoro tekniği kullanın
        • Günlük hedefler belirleyin
        • İlerlemenizi takip edin
        """
    else:  # motivation
        return f"""
        🌟 Motivasyon Mesajı
        
        Şu anki puanınız {latest_score.total_score:.1f} ve %{latest_score.percentile:.1f} dilimdesiniz!
        
        💪 Güçlü Yanlarınız:
        {chr(10).join([f'• {subject}' for subject in strong_subjects]) if strong_subjects else '• Kararlı ve azimli bir öğrencisiniz'}
        
        🎯 Hedeflerinize Odaklanın:
        • Her gün biraz daha iyiye gidiyorsunuz
        • Sabır ve çalışma her zaman meyvesini verir
        • Başarı bir süreçtir, sonuç değil
        
        🚀 Unutmayın: En büyük rakibiniz dünkü halinizdir!
        """

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Kullanıcı adı ve şifre gerekli'})
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten alınmış'})
        
        if email and User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Bu e-posta adresi zaten kayıtlı'})
        
        user = User(
            username=username,
            email=email if email else None,
            password_hash=generate_password_hash(password)
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True, 'message': 'Kayıt başarılı'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Kayıt sırasında hata oluştu'})
    
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            user.last_login = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'message': 'Giriş başarılı'})
        else:
            return jsonify({'success': False, 'message': 'Kullanıcı adı veya şifre yanlış'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    recent_scores = Score.query.filter_by(user_id=user.id).order_by(Score.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', user=user, recent_scores=recent_scores)

@app.route('/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        data = request.get_json()
        
        # Validate input data
        subjects = ['turkce', 'matematik', 'fen', 'inkilap', 'din', 'ingilizce']
        max_questions = {'turkce': 20, 'matematik': 20, 'fen': 20, 'inkilap': 10, 'din': 10, 'ingilizce': 10}
        
        for subject in subjects:
            dogru = data.get(f'{subject}_dogru', 0)
            yanlis = data.get(f'{subject}_yanlis', 0)
            max_q = max_questions[subject]
            
            if dogru < 0 or yanlis < 0 or dogru > max_q or yanlis > max_q:
                return jsonify({'success': False, 'message': f'{subject.title()} için geçersiz değer'})
            
            if dogru + yanlis > max_q:
                return jsonify({'success': False, 'message': f'{subject.title()} için toplam soru sayısı {max_q}\'yi geçemez'})
        
        # Calculate score
        result = calculate_score(data)
        
        # Save to database
        score = Score(
            user_id=session['user_id'],
            turkce_dogru=data.get('turkce_dogru', 0),
            turkce_yanlis=data.get('turkce_yanlis', 0),
            matematik_dogru=data.get('matematik_dogru', 0),
            matematik_yanlis=data.get('matematik_yanlis', 0),
            fen_dogru=data.get('fen_dogru', 0),
            fen_yanlis=data.get('fen_yanlis', 0),
            inkilap_dogru=data.get('inkilap_dogru', 0),
            inkilap_yanlis=data.get('inkilap_yanlis', 0),
            din_dogru=data.get('din_dogru', 0),
            din_yanlis=data.get('din_yanlis', 0),
            ingilizce_dogru=data.get('ingilizce_dogru', 0),
            ingilizce_yanlis=data.get('ingilizce_yanlis', 0),
            total_score=result['total_score'],
            percentile=result['percentile']
        )
        
        db.session.add(score)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'result': result,
            'message': 'Puan başarıyla hesaplandı'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Hesaplama hatası: {str(e)}'})

@app.route('/ai-recommendations')
@login_required
def ai_recommendations():
    recommendation_type = request.args.get('type', 'study_plan')
    
    # Get user's recent scores for context
    user_scores = Score.query.filter_by(user_id=session['user_id']).order_by(Score.created_at.desc()).limit(5).all()
    
    # Get AI recommendation
    recommendation = get_ai_recommendation(user_scores, recommendation_type)
    
    # Save to database
    ai_rec = AIRecommendation(
        user_id=session['user_id'],
        recommendation_type=recommendation_type,
        content=recommendation
    )
    db.session.add(ai_rec)
    db.session.commit()
    
    return jsonify({'recommendation': recommendation})

@app.route('/analytics')
@login_required
def analytics():
    user_scores = Score.query.filter_by(user_id=session['user_id']).order_by(Score.created_at.asc()).all()
    
    analytics_data = {
        'score_history': [{'date': score.created_at.strftime('%Y-%m-%d'), 'score': score.total_score} for score in user_scores],
        'subject_performance': {},
        'improvement_trend': []
    }
    
    if user_scores:
        latest_score = user_scores[-1]
        subjects = ['turkce', 'matematik', 'fen', 'inkilap', 'din', 'ingilizce']
        max_questions = {'turkce': 20, 'matematik': 20, 'fen': 20, 'inkilap': 10, 'din': 10, 'ingilizce': 10}
        
        for subject in subjects:
            dogru = getattr(latest_score, f'{subject}_dogru', 0)
            max_q = max_questions[subject]
            success_rate = (dogru / max_q) * 100 if max_q > 0 else 0
            analytics_data['subject_performance'][subject] = round(success_rate, 1)
        
        # Calculate improvement trend
        if len(user_scores) > 1:
            first_score = user_scores[0].total_score
            latest_score_val = latest_score.total_score
            improvement = latest_score_val - first_score
            analytics_data['improvement_trend'] = {
                'total_improvement': round(improvement, 2),
                'average_per_attempt': round(improvement / len(user_scores), 2)
            }
    
    return jsonify(analytics_data)

@app.route('/study-session', methods=['POST'])
@login_required
def log_study_session():
    try:
        data = request.get_json()
        
        session_log = StudySession(
            user_id=session['user_id'],
            subject=data.get('subject', ''),
            duration_minutes=data.get('duration', 0),
            topics_studied=data.get('topics', ''),
            difficulty_level=data.get('difficulty', 'medium')
        )
        
        db.session.add(session_log)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Çalışma seansı kaydedildi'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Kayıt hatası: {str(e)}'})

@app.route('/school-recommendations')
@login_required
def school_recommendations():
    user_score = request.args.get('score', type=float)
    city = request.args.get('city', '')
    school_type = request.args.get('type', '')
    
    # Get user's latest score if not provided
    if not user_score:
        latest_score = Score.query.filter_by(user_id=session['user_id']).order_by(Score.created_at.desc()).first()
        if latest_score:
            user_score = latest_score.total_score
        else:
            user_score = 0
    
    # Build query
    query = School.query.filter(
        School.min_score <= user_score + 20,  # Include schools slightly above score
        School.max_score >= user_score - 50   # Include schools within reach
    )
    
    if city:
        query = query.filter(School.city.ilike(f'%{city}%'))
    if school_type:
        query = query.filter(School.school_type.ilike(f'%{school_type}%'))
    
    schools = query.order_by(School.min_score.desc()).limit(20).all()
    
    # Categorize schools
    safe_schools = [s for s in schools if s.min_score <= user_score - 20]
    target_schools = [s for s in schools if s.min_score > user_score - 20 and s.min_score <= user_score + 10]
    reach_schools = [s for s in schools if s.min_score > user_score + 10]
    
    return jsonify({
        'user_score': user_score,
        'safe_schools': [{'id': s.id, 'name': s.name, 'city': s.city, 'district': s.district, 
                         'type': s.school_type, 'min_score': s.min_score, 'quota': s.quota} for s in safe_schools],
        'target_schools': [{'id': s.id, 'name': s.name, 'city': s.city, 'district': s.district, 
                           'type': s.school_type, 'min_score': s.min_score, 'quota': s.quota} for s in target_schools],
        'reach_schools': [{'id': s.id, 'name': s.name, 'city': s.city, 'district': s.district, 
                          'type': s.school_type, 'min_score': s.min_score, 'quota': s.quota} for s in reach_schools]
    })

@app.route('/mock-exam', methods=['GET', 'POST'])
@login_required
def mock_exam():
    if request.method == 'POST':
        data = request.get_json()
        
        # Save mock exam results
        mock_exam = MockExam(
            user_id=session['user_id'],
            exam_name=data.get('exam_name', 'Mock Exam'),
            total_questions=data.get('total_questions', 90),
            correct_answers=data.get('correct_answers', 0),
            wrong_answers=data.get('wrong_answers', 0),
            empty_answers=data.get('empty_answers', 0),
            time_spent=data.get('time_spent', 0),
            subject_scores=data.get('subject_scores', {})
        )
        db.session.add(mock_exam)
        
        # Check for achievements
        check_achievements(session['user_id'], 'mock_exam', data)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Mock exam results saved!'})
    
    # GET request - return mock exam history
    exams = MockExam.query.filter_by(user_id=session['user_id']).order_by(MockExam.created_at.desc()).limit(10).all()
    return jsonify({
        'exams': [{
            'id': e.id,
            'name': e.exam_name,
            'total_questions': e.total_questions,
            'correct_answers': e.correct_answers,
            'wrong_answers': e.wrong_answers,
            'time_spent': e.time_spent,
            'created_at': e.created_at.strftime('%Y-%m-%d %H:%M')
        } for e in exams]
    })

@app.route('/study-plan', methods=['GET', 'POST'])
@login_required
def study_plan():
    if request.method == 'POST':
        data = request.get_json()
        
        # Deactivate old plans
        StudyPlan.query.filter_by(user_id=session['user_id'], is_active=True).update({'is_active': False})
        
        # Create new study plan
        plan = StudyPlan(
            user_id=session['user_id'],
            plan_name=data.get('plan_name', 'My Study Plan'),
            target_score=data.get('target_score', 500),
            target_date=datetime.strptime(data.get('target_date'), '%Y-%m-%d').date(),
            daily_study_hours=data.get('daily_study_hours', 4),
            subjects_focus=data.get('subjects_focus', {})
        )
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Study plan created!'})
    
    # GET request - return active study plan
    plan = StudyPlan.query.filter_by(user_id=session['user_id'], is_active=True).first()
    if plan:
        return jsonify({
            'id': plan.id,
            'name': plan.plan_name,
            'target_score': plan.target_score,
            'target_date': plan.target_date.strftime('%Y-%m-%d'),
            'daily_study_hours': plan.daily_study_hours,
            'subjects_focus': plan.subjects_focus
        })
    return jsonify({'plan': None})

@app.route('/achievements')
@login_required
def achievements():
    user_achievements = Achievement.query.filter_by(user_id=session['user_id']).order_by(Achievement.earned_at.desc()).all()
    return jsonify({
        'achievements': [{
            'id': a.id,
            'type': a.achievement_type,
            'title': a.title,
            'description': a.description,
            'badge_icon': a.badge_icon,
            'earned_at': a.earned_at.strftime('%Y-%m-%d %H:%M')
        } for a in user_achievements]
    })

def check_achievements(user_id, action_type, data):
    """Check and award achievements based on user actions"""
    achievements_to_add = []
    
    if action_type == 'score_calculation':
        score = data.get('total_score', 0)
        if score >= 450:
            achievements_to_add.append({
                'type': 'high_score',
                'title': 'Yüksek Puan Ustası',
                'description': '450+ puan aldınız! Harika bir başarı!',
                'badge_icon': 'fas fa-trophy'
            })
        elif score >= 400:
            achievements_to_add.append({
                'type': 'good_score',
                'title': 'İyi Puan',
                'description': '400+ puan aldınız! Çok iyi gidiyorsunuz!',
                'badge_icon': 'fas fa-medal'
            })
    
    elif action_type == 'mock_exam':
        correct_answers = data.get('correct_answers', 0)
        if correct_answers >= 80:
            achievements_to_add.append({
                'type': 'mock_master',
                'title': 'Deneme Ustası',
                'description': '80+ doğru cevap! Mükemmel performans!',
                'badge_icon': 'fas fa-star'
            })
    
    # Add achievements to database
    for achievement_data in achievements_to_add:
        # Check if user already has this achievement
        existing = Achievement.query.filter_by(
            user_id=user_id,
            achievement_type=achievement_data['type']
        ).first()
        
        if not existing:
            achievement = Achievement(
                user_id=user_id,
                achievement_type=achievement_data['type'],
                title=achievement_data['title'],
                description=achievement_data['description'],
                badge_icon=achievement_data['badge_icon']
            )
            db.session.add(achievement)

def populate_sample_schools():
    """Populate database with sample schools"""
    if School.query.count() == 0:
        sample_schools = [
            {'name': 'Galatasaray Lisesi', 'city': 'İstanbul', 'district': 'Beyoğlu', 'school_type': 'Anadolu Lisesi', 'min_score': 480, 'max_score': 500, 'quota': 120},
            {'name': 'Robert Kolej', 'city': 'İstanbul', 'district': 'Arnavutköy', 'school_type': 'Özel Lise', 'min_score': 470, 'max_score': 495, 'quota': 200},
            {'name': 'Ankara Fen Lisesi', 'city': 'Ankara', 'district': 'Çankaya', 'school_type': 'Fen Lisesi', 'min_score': 460, 'max_score': 485, 'quota': 180},
            {'name': 'İzmir Fen Lisesi', 'city': 'İzmir', 'district': 'Konak', 'school_type': 'Fen Lisesi', 'min_score': 450, 'max_score': 475, 'quota': 160},
            {'name': 'Kadıköy Anadolu Lisesi', 'city': 'İstanbul', 'district': 'Kadıköy', 'school_type': 'Anadolu Lisesi', 'min_score': 420, 'max_score': 450, 'quota': 240},
            {'name': 'Bursa Anadolu Lisesi', 'city': 'Bursa', 'district': 'Osmangazi', 'school_type': 'Anadolu Lisesi', 'min_score': 400, 'max_score': 430, 'quota': 200},
            {'name': 'Antalya Sosyal Bilimler Lisesi', 'city': 'Antalya', 'district': 'Muratpaşa', 'school_type': 'Sosyal Bilimler Lisesi', 'min_score': 380, 'max_score': 410, 'quota': 180},
            {'name': 'Adana Fen Lisesi', 'city': 'Adana', 'district': 'Seyhan', 'school_type': 'Fen Lisesi', 'min_score': 440, 'max_score': 465, 'quota': 150},
            {'name': 'Trabzon Anadolu Lisesi', 'city': 'Trabzon', 'district': 'Ortahisar', 'school_type': 'Anadolu Lisesi', 'min_score': 360, 'max_score': 390, 'quota': 220},
            {'name': 'Eskişehir Fen Lisesi', 'city': 'Eskişehir', 'district': 'Odunpazarı', 'school_type': 'Fen Lisesi', 'min_score': 430, 'max_score': 455, 'quota': 140},
            {'name': 'Konya Fen Lisesi', 'city': 'Konya', 'district': 'Selçuklu', 'school_type': 'Fen Lisesi', 'min_score': 425, 'max_score': 450, 'quota': 160},
            {'name': 'Gaziantep Anadolu Lisesi', 'city': 'Gaziantep', 'district': 'Şahinbey', 'school_type': 'Anadolu Lisesi', 'min_score': 370, 'max_score': 400, 'quota': 200},
            {'name': 'Kayseri Fen Lisesi', 'city': 'Kayseri', 'district': 'Melikgazi', 'school_type': 'Fen Lisesi', 'min_score': 415, 'max_score': 440, 'quota': 140},
            {'name': 'Samsun Anadolu Lisesi', 'city': 'Samsun', 'district': 'İlkadım', 'school_type': 'Anadolu Lisesi', 'min_score': 350, 'max_score': 380, 'quota': 180},
            {'name': 'Mersin Fen Lisesi', 'city': 'Mersin', 'district': 'Yenişehir', 'school_type': 'Fen Lisesi', 'min_score': 410, 'max_score': 435, 'quota': 130}
        ]
        
        for school_data in sample_schools:
            school = School(**school_data)
            db.session.add(school)
        
        db.session.commit()

# Initialize database
def create_tables():
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

# Static file routes for production
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/robots.txt')
def robots_txt():
    return app.send_static_file('robots.txt')

@app.route('/sitemap.xml')
def sitemap_xml():
    from flask import Response
    
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{}/</loc>
        <lastmod>{}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{}/login</loc>
        <lastmod>{}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{}/dashboard</loc>
        <lastmod>{}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
</urlset>'''.format(
        request.url_root.rstrip('/'),
        datetime.utcnow().strftime('%Y-%m-%d'),
        request.url_root.rstrip('/'),
        datetime.utcnow().strftime('%Y-%m-%d'),
        request.url_root.rstrip('/'),
        datetime.utcnow().strftime('%Y-%m-%d')
    )
    
    return Response(sitemap_xml, mimetype='application/xml')

if __name__ == '__main__':
    # Initialize database with error handling
    try:
        with app.app_context():
            db.create_all()
            populate_sample_schools()
            print("Application initialized successfully")
    except Exception as e:
        print(f"Initialization error: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    debug = not os.environ.get('DATABASE_URL')  # Production mode if DATABASE_URL exists
    app.run(debug=debug, host='0.0.0.0', port=port)
