// Main JavaScript functionality for LGS Score Calculator

// Utility functions
function showAlert(message, type = 'danger', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
}

function showLoading(show = true) {
    const modal = document.getElementById('loadingModal');
    if (modal) {
        if (show) {
            new bootstrap.Modal(modal).show();
        } else {
            bootstrap.Modal.getInstance(modal)?.hide();
        }
    }
}

function createConfetti() {
    const colors = ['#ff6b6b', '#4ecdc4', '#45aaf2', '#feca57', '#a55eea', '#26de81'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
        confetti.style.animationDelay = Math.random() * 2 + 's';
        document.body.appendChild(confetti);
        
        setTimeout(() => {
            if (confetti.parentNode) {
                confetti.remove();
            }
        }, 5000);
    }
}

// Form validation
function validateSubjectInputs(subject, maxQuestions) {
    const dogruInput = document.querySelector(`input[name="${subject}_dogru"]`);
    const yanlisInput = document.querySelector(`input[name="${subject}_yanlis"]`);
    
    if (!dogruInput || !yanlisInput) return true;
    
    const dogru = parseInt(dogruInput.value) || 0;
    const yanlis = parseInt(yanlisInput.value) || 0;
    
    // Validate individual limits
    if (dogru < 0 || dogru > maxQuestions) {
        dogruInput.value = Math.max(0, Math.min(maxQuestions, dogru));
        return false;
    }
    
    if (yanlis < 0 || yanlis > maxQuestions) {
        yanlisInput.value = Math.max(0, Math.min(maxQuestions, yanlis));
        return false;
    }
    
    // Validate total doesn't exceed max
    if (dogru + yanlis > maxQuestions) {
        if (dogruInput === document.activeElement) {
            yanlisInput.value = Math.max(0, maxQuestions - dogru);
        } else {
            dogruInput.value = Math.max(0, maxQuestions - yanlis);
        }
        return false;
    }
    
    return true;
}

function validateAllInputs() {
    const subjects = [
        { name: 'turkce', max: 20 },
        { name: 'matematik', max: 20 },
        { name: 'fen', max: 20 },
        { name: 'inkilap', max: 10 },
        { name: 'din', max: 10 },
        { name: 'ingilizce', max: 10 }
    ];
    
    let isValid = true;
    subjects.forEach(subject => {
        if (!validateSubjectInputs(subject.name, subject.max)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Add input event listeners for real-time validation
function setupInputValidation() {
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const name = this.name;
            const subject = name.split('_')[0];
            const maxQuestions = ['turkce', 'matematik', 'fen'].includes(subject) ? 20 : 10;
            validateSubjectInputs(subject, maxQuestions);
        });
        
        input.addEventListener('blur', function() {
            validateAllInputs();
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupInputValidation();
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
            }
        });
    }, observerOptions);
    
    // Observe all cards
    document.querySelectorAll('.stat-card, .subject-card, .result-card').forEach(card => {
        observer.observe(card);
    });
});

// Export functions for use in other scripts
window.LGSUtils = {
    showAlert,
    showLoading,
    createConfetti,
    validateAllInputs,
    validateSubjectInputs
};
