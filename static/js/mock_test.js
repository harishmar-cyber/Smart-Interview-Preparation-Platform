// Timed Mock Test Engine

let currentQuestionIndex = 0;
const userAnswers = {};
const reviewFlags = {};
let timerInterval = null;

function initMockTest(testData) {
    const { attemptId, questions, remainingSeconds, totalSeconds, savedAnswers } = testData;

    // Prepopulate saved answers
    if (savedAnswers) {
        Object.keys(savedAnswers).forEach(qId => {
            if (savedAnswers[qId]) {
                userAnswers[qId] = savedAnswers[qId];
            }
        });
    }

    let timeLeft = remainingSeconds;
    const timerDisplay = document.getElementById('timerCountdown');

    // 1. Start Countdown
    function updateTimer() {
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            timerDisplay.innerText = "00:00";
            showToast("Time has expired! Submitting test automatically...", "warning");
            submitTestAutomatically(attemptId);
            return;
        }

        const mins = Math.floor(timeLeft / 60);
        const secs = timeLeft % 60;
        timerDisplay.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        if (timeLeft < 180) { // Less than 3 mins
            timerDisplay.classList.add('timer-warning');
        }

        timeLeft--;
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);

    // 2. Render initial question
    renderQuestion(0, questions);
    updatePalette(questions);

    // 3. Navigation Buttons
    const prevBtn = document.getElementById('prevQuestionBtn');
    const nextBtn = document.getElementById('nextQuestionBtn');
    const clearBtn = document.getElementById('clearAnswerBtn');
    const reviewBtn = document.getElementById('markReviewBtn');
    const submitBtn = document.getElementById('submitTestBtn');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentQuestionIndex > 0) {
                currentQuestionIndex--;
                renderQuestion(currentQuestionIndex, questions);
                updatePalette(questions);
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentQuestionIndex < questions.length - 1) {
                currentQuestionIndex++;
                renderQuestion(currentQuestionIndex, questions);
                updatePalette(questions);
            }
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            const currentQ = questions[currentQuestionIndex];
            delete userAnswers[currentQ.id];
            renderQuestion(currentQuestionIndex, questions);
            updatePalette(questions);
        });
    }

    if (reviewBtn) {
        reviewBtn.addEventListener('click', () => {
            const currentQ = questions[currentQuestionIndex];
            reviewFlags[currentQ.id] = !reviewFlags[currentQ.id];
            renderQuestion(currentQuestionIndex, questions);
            updatePalette(questions);
        });
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', () => {
            // Populate summary modal
            const answeredCount = Object.keys(userAnswers).filter(k => userAnswers[k]).length;
            const unansweredCount = questions.length - answeredCount;
            const reviewCount = Object.keys(reviewFlags).filter(k => reviewFlags[k]).length;

            document.getElementById('modalAnsweredCount').innerText = answeredCount;
            document.getElementById('modalUnansweredCount').innerText = unansweredCount;
            document.getElementById('modalReviewCount').innerText = reviewCount;

            const submitModal = new bootstrap.Modal(document.getElementById('confirmSubmitModal'));
            submitModal.show();
        });
    }

    const confirmFinalSubmitBtn = document.getElementById('confirmFinalSubmitBtn');
    if (confirmFinalSubmitBtn) {
        confirmFinalSubmitBtn.addEventListener('click', () => {
            confirmFinalSubmitBtn.disabled = true;
            confirmFinalSubmitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Submitting...';
            submitTestToServer(attemptId, totalSeconds - timeLeft);
        });
    }
}

function renderQuestion(index, questions) {
    const q = questions[index];
    currentQuestionIndex = index;

    document.getElementById('questionCounterText').innerText = `Question ${index + 1} of ${questions.length}`;
    document.getElementById('questionDifficultyBadge').innerText = q.difficulty;
    document.getElementById('questionMarksBadge').innerText = `${q.marks} Mark${q.marks > 1 ? 's' : ''}`;
    document.getElementById('questionCategoryText').innerText = q.category_name;
    document.getElementById('questionBodyText').innerText = q.question_text;

    // Render Options
    const optionsContainer = document.getElementById('optionsListContainer');
    optionsContainer.innerHTML = '';

    const options = [
        { key: 'A', text: q.option_a },
        { key: 'B', text: q.option_b },
        { key: 'C', text: q.option_c },
        { key: 'D', text: q.option_d }
    ];

    const currentSelected = userAnswers[q.id];

    options.forEach(opt => {
        if (!opt.text) return;

        const isChecked = currentSelected === opt.key;
        const optHtml = `
            <div class="option-item">
                <input type="radio" class="d-none option-input" name="option_choice" id="opt_${opt.key}" value="${opt.key}" ${isChecked ? 'checked' : ''}>
                <label for="opt_${opt.key}" class="option-label">
                    <span class="option-prefix">${opt.key}</span>
                    <span class="option-text fw-medium">${escapeHtml(opt.text)}</span>
                </label>
            </div>
        `;
        optionsContainer.insertAdjacentHTML('beforeend', optHtml);
    });

    // Option change listener
    document.querySelectorAll('input[name="option_choice"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            userAnswers[q.id] = e.target.value;
            updatePalette(questions);
        });
    });

    // Mark review button state
    const isReview = reviewFlags[q.id];
    const reviewBtn = document.getElementById('markReviewBtn');
    if (reviewBtn) {
        if (isReview) {
            reviewBtn.classList.remove('btn-outline-warning');
            reviewBtn.classList.add('btn-warning');
            reviewBtn.innerHTML = '<i class="fas fa-flag me-1"></i> Marked for Review';
        } else {
            reviewBtn.classList.remove('btn-warning');
            reviewBtn.classList.add('btn-outline-warning');
            reviewBtn.innerHTML = '<i class="far fa-flag me-1"></i> Mark for Review';
        }
    }

    // Prev / Next button states
    const prevBtn = document.getElementById('prevQuestionBtn');
    const nextBtn = document.getElementById('nextQuestionBtn');
    if (prevBtn) prevBtn.disabled = (index === 0);
    if (nextBtn) nextBtn.disabled = (index === questions.length - 1);
}

function updatePalette(questions) {
    const paletteGrid = document.getElementById('questionPaletteGrid');
    if (!paletteGrid) return;

    paletteGrid.innerHTML = '';
    questions.forEach((q, idx) => {
        const isAnswered = !!userAnswers[q.id];
        const isReview = !!reviewFlags[q.id];
        const isCurrent = idx === currentQuestionIndex;

        let statusClass = '';
        if (isReview) statusClass = 'palette-review';
        else if (isAnswered) statusClass = 'palette-answered';

        if (isCurrent) statusClass += ' palette-current';

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `question-palette-btn ${statusClass}`;
        btn.innerText = idx + 1;
        btn.addEventListener('click', () => {
            renderQuestion(idx, questions);
            updatePalette(questions);
        });
        paletteGrid.appendChild(btn);
    });

    // Update Counts Summary
    const answeredCount = Object.keys(userAnswers).filter(k => userAnswers[k]).length;
    document.getElementById('paletteAnsweredCount').innerText = answeredCount;
    document.getElementById('paletteUnansweredCount').innerText = questions.length - answeredCount;
    document.getElementById('paletteReviewCount').innerText = Object.keys(reviewFlags).filter(k => reviewFlags[k]).length;
}

async function submitTestToServer(attemptId, timeTakenSeconds) {
    try {
        const response = await fetch(`/mock-tests/attempt/${attemptId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                answers: userAnswers,
                time_taken_seconds: Math.max(1, Math.round(timeTakenSeconds))
            })
        });

        const data = await response.json();
        if (data.success && data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            alert(data.message || 'Error submitting test.');
        }
    } catch (err) {
        console.error('Submission error:', err);
        alert('Network error submitting your test. Please try again.');
    }
}

function submitTestAutomatically(attemptId) {
    submitTestToServer(attemptId, 1800);
}

function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
}
