// Dashboard specific JavaScript functionality

let scoreChart = null;
let subjectChart = null;

// Calculator form handler
document.getElementById('calculatorForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!window.LGSUtils.validateAllInputs()) {
        window.LGSUtils.showAlert('Lütfen geçerli değerler girin', 'warning');
        return;
    }
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    // Convert to integers
    Object.keys(data).forEach(key => {
        data[key] = parseInt(data[key]) || 0;
    });
    
    window.LGSUtils.showLoading(true);
    
    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.result);
            window.LGSUtils.showAlert('Puan başarıyla hesaplandı!', 'success');
            updateStats();
            
            // Show confetti for good scores
            if (result.result.total_score > 400) {
                setTimeout(() => window.LGSUtils.createConfetti(), 500);
            }
        } else {
            window.LGSUtils.showAlert(result.message, 'danger');
        }
    } catch (error) {
        window.LGSUtils.showAlert('Hesaplama sırasında hata oluştu', 'danger');
        console.error('Error:', error);
    } finally {
        window.LGSUtils.showLoading(false);
    }
});

function displayResults(result) {
    const resultsDiv = document.getElementById('results');
    const totalScore = document.getElementById('totalScore');
    const percentileValue = document.getElementById('percentileValue');
    const scoreProgress = document.getElementById('scoreProgress');
    
    // Show results section
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
    
    // Animate score counting
    animateNumber(totalScore, 0, result.total_score, 1500);
    animateNumber(percentileValue, 0, result.percentile, 1500, '%');
    
    // Update progress bar
    const progressPercent = (result.total_score / 500) * 100;
    setTimeout(() => {
        scoreProgress.style.width = Math.min(progressPercent, 100) + '%';
    }, 500);
    
    // Update net results
    Object.keys(result.nets).forEach(subject => {
        const element = document.getElementById(subject + 'Net');
        if (element) {
            animateNumber(element, 0, result.nets[subject], 1000);
        }
    });
}

function animateNumber(element, start, end, duration, suffix = '') {
    const startTime = performance.now();
    const difference = end - start;
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (difference * easeOutCubic(progress));
        element.textContent = current.toFixed(2) + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}

function resetForm() {
    document.getElementById('calculatorForm').reset();
    document.getElementById('results').style.display = 'none';
    
    // Reset all number inputs to 0
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.value = 0;
    });
    
    window.LGSUtils.showAlert('Form sıfırlandı', 'info', 2000);
}

// AI Recommendations
async function getAIRecommendation(type) {
    const recommendationsDiv = document.getElementById('aiRecommendations');
    
    recommendationsDiv.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">AI önerisi hazırlanıyor...</span>
            </div>
            <p class="mt-2">AI öneriniz hazırlanıyor...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/ai-recommendations?type=${type}`);
        const result = await response.json();
        
        if (result.success) {
            displayAIRecommendation(result.recommendation, type);
        } else {
            recommendationsDiv.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${result.message}
                </div>
            `;
        }
    } catch (error) {
        recommendationsDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                AI önerisi alınırken hata oluştu. Lütfen tekrar deneyin.
            </div>
        `;
        console.error('AI Recommendation Error:', error);
    }
}

function displayAIRecommendation(recommendation, type) {
    const recommendationsDiv = document.getElementById('aiRecommendations');
    
    const typeIcons = {
        'study_plan': 'fas fa-calendar-alt',
        'improvement': 'fas fa-arrow-up',
        'motivation': 'fas fa-heart'
    };
    
    const typeTitles = {
        'study_plan': 'Çalışma Planı',
        'improvement': 'Gelişim Önerileri',
        'motivation': 'Motivasyon Mesajı'
    };
    
    recommendationsDiv.innerHTML = `
        <div class="ai-recommendation">
            <h5><i class="${typeIcons[type]} me-2"></i>${typeTitles[type]}</h5>
            <div class="recommendation-content">${recommendation.replace(/\n/g, '<br>')}</div>
            <small class="text-muted mt-2 d-block">
                <i class="fas fa-clock me-1"></i>
                ${new Date().toLocaleString('tr-TR')} tarihinde oluşturuldu
            </small>
        </div>
    `;
}

// Analytics
async function loadAnalytics() {
    try {
        const response = await fetch('/analytics');
        const data = await response.json();
        
        createScoreChart(data.score_history);
        createSubjectChart(data.subject_performance);
        
    } catch (error) {
        console.error('Analytics loading error:', error);
    }
}

function createScoreChart(scoreHistory) {
    const ctx = document.getElementById('scoreChart');
    if (!ctx || scoreHistory.length === 0) return;
    
    if (scoreChart) {
        scoreChart.destroy();
    }
    
    scoreChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: scoreHistory.map(item => item.date),
            datasets: [{
                label: 'Puan Gelişimi',
                data: scoreHistory.map(item => item.score),
                borderColor: '#0066cc',
                backgroundColor: 'rgba(0, 102, 204, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Puan Gelişim Grafiği'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 100,
                    max: 500,
                    title: {
                        display: true,
                        text: 'Puan'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Tarih'
                    }
                }
            }
        }
    });
}

function createSubjectChart(subjectPerformance) {
    const ctx = document.getElementById('subjectChart');
    if (!ctx || Object.keys(subjectPerformance).length === 0) return;
    
    if (subjectChart) {
        subjectChart.destroy();
    }
    
    const subjects = Object.keys(subjectPerformance);
    const scores = Object.values(subjectPerformance);
    
    const subjectNames = {
        'turkce': 'Türkçe',
        'matematik': 'Matematik',
        'fen': 'Fen',
        'inkilap': 'İnkılap',
        'din': 'Din',
        'ingilizce': 'İngilizce'
    };
    
    subjectChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: subjects.map(s => subjectNames[s] || s),
            datasets: [{
                label: 'Başarı Oranı (%)',
                data: scores,
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.2)',
                borderWidth: 2,
                pointBackgroundColor: '#28a745',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Ders Bazında Performans'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            }
        }
    });
}

// Update stats after calculation
async function updateStats() {
    try {
        const response = await fetch('/analytics');
        const data = await response.json();
        
        if (data.score_history && data.score_history.length > 0) {
            const scores = data.score_history.map(item => item.score);
            const totalAttempts = scores.length;
            const bestScore = Math.max(...scores);
            const averageScore = scores.reduce((a, b) => a + b, 0) / scores.length;
            
            document.getElementById('totalAttempts').textContent = totalAttempts;
            document.getElementById('bestScore').textContent = bestScore.toFixed(2);
            document.getElementById('averageScore').textContent = averageScore.toFixed(2);
        }
    } catch (error) {
        console.error('Stats update error:', error);
    }
}

// Tab change handler
document.addEventListener('shown.bs.tab', function (event) {
    const targetId = event.target.getAttribute('data-bs-target');
    if (targetId === '#analytics') {
        loadAnalytics();
    }
});

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Load analytics if analytics tab is active
    if (document.getElementById('analytics-tab').classList.contains('active')) {
        loadAnalytics();
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl + Enter to calculate
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('calculatorForm').dispatchEvent(new Event('submit'));
        }
        
        // Ctrl + R to reset form
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            resetForm();
        }
    });
    
    // Add tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
