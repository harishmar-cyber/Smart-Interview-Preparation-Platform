// Smart Interview Preparation Platform - Main Interactive Script

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Bootstrap Tooltips & Toasts
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(el => new bootstrap.Tooltip(el));

        const toastElList = [].slice.call(document.querySelectorAll('.toast'));
        toastElList.map(toastEl => {
            const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
            toast.show();
        });
    }

    // 2. Mobile Sidebar Toggle
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const appSidebar = document.querySelector('.app-sidebar');
    if (sidebarToggleBtn && appSidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            appSidebar.classList.toggle('show');
        });
    }

    // 3. Scroll Triggered Animations via IntersectionObserver
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    if ('IntersectionObserver' in window && animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-up');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animatedElements.forEach(el => observer.observe(el));
    }

    // 4. Animated Counters for Stat Numbers
    const counters = document.querySelectorAll('.stat-counter');
    counters.forEach(counter => {
        const target = +counter.getAttribute('data-target') || 0;
        const duration = 1200; // ms
        const stepTime = 20;
        const totalSteps = duration / stepTime;
        const increment = target / totalSteps;
        let current = 0;

        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.innerText = Math.ceil(current);
                setTimeout(updateCounter, stepTime);
            } else {
                counter.innerText = target;
            }
        };
        updateCounter();
    });

    // 5. Bookmark Toggle AJAX Handler
    document.querySelectorAll('.btn-bookmark-toggle').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const questionId = btn.getAttribute('data-question-id');
            if (!questionId) return;

            try {
                const response = await fetch(`/questions/${questionId}/bookmark`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const data = await response.json();
                if (data.success) {
                    const icon = btn.querySelector('i');
                    if (data.bookmarked) {
                        icon.classList.remove('far');
                        icon.classList.add('fas', 'text-warning');
                        btn.setAttribute('title', 'Remove Bookmark');
                    } else {
                        icon.classList.remove('fas', 'text-warning');
                        icon.classList.add('far');
                        btn.setAttribute('title', 'Bookmark Question');
                    }
                    showToast(data.message, 'info');
                }
            } catch (err) {
                console.error('Bookmark error:', err);
            }
        });
    });
});

// Utility to display floating toast notification
function showToast(message, type = 'info') {
    let container = document.getElementById('globalToastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'globalToastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
    }

    const toastDiv = document.createElement('div');
    toastDiv.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : (type === 'success' ? 'success' : 'primary')} border-0 shadow-lg`;
    toastDiv.setAttribute('role', 'alert');
    toastDiv.setAttribute('aria-live', 'assertive');
    toastDiv.setAttribute('aria-atomic', 'true');
    toastDiv.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fw-semibold">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    container.appendChild(toastDiv);
    const bsToast = new bootstrap.Toast(toastDiv, { delay: 3500 });
    bsToast.show();
    toastDiv.addEventListener('hidden.bs.toast', () => toastDiv.remove());
}
