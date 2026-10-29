// Chart.js Visual Analytics Engine

document.addEventListener('DOMContentLoaded', () => {
    initAnalyticsCharts();
});

async function initAnalyticsCharts() {
    const trendCtx = document.getElementById('scoreTrendChart');
    const categoryCtx = document.getElementById('categoryBarChart');
    const distCtx = document.getElementById('distributionDonutChart');

    if (!trendCtx && !categoryCtx && !distCtx) return;

    try {
        const response = await fetch('/api/analytics-data');
        const data = await response.json();

        // 1. Performance Trend Line Chart
        if (trendCtx) {
            new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: data.trend.labels.length > 0 ? data.trend.labels : ['Test 1'],
                    datasets: [{
                        label: 'Score Percentage (%)',
                        data: data.trend.data.length > 0 ? data.trend.data : [75],
                        borderColor: '#6366F1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointBackgroundColor: '#8B5CF6',
                        pointBorderColor: '#FFFFFF',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => ` Score: ${context.parsed.y}%`
                            }
                        }
                    },
                    scales: {
                        y: {
                            min: 0,
                            max: 100,
                            grid: { color: 'rgba(226, 232, 240, 0.6)' },
                            ticks: { callback: (val) => val + '%' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        // 2. Category Accuracy Bar Chart
        if (categoryCtx) {
            new Chart(categoryCtx, {
                type: 'bar',
                data: {
                    labels: data.categories.labels.length > 0 ? data.categories.labels : ['Java', 'DBMS', 'OS', 'Aptitude', 'Networks'],
                    datasets: [{
                        label: 'Accuracy (%)',
                        data: data.categories.data.length > 0 ? data.categories.data : [80, 85, 70, 75, 65],
                        backgroundColor: [
                            'rgba(99, 102, 241, 0.85)',
                            'rgba(139, 92, 246, 0.85)',
                            'rgba(6, 182, 212, 0.85)',
                            'rgba(16, 185, 129, 0.85)',
                            'rgba(251, 113, 133, 0.85)',
                            'rgba(245, 158, 11, 0.85)'
                        ],
                        borderRadius: 8,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            min: 0,
                            max: 100,
                            grid: { color: 'rgba(226, 232, 240, 0.6)' },
                            ticks: { callback: (val) => val + '%' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        // 3. Preparation Distribution Doughnut Chart
        if (distCtx) {
            new Chart(distCtx, {
                type: 'doughnut',
                data: {
                    labels: data.distribution.labels,
                    datasets: [{
                        data: data.distribution.data,
                        backgroundColor: ['#6366F1', '#06B6D4', '#10B981', '#8B5CF6'],
                        borderWidth: 2,
                        borderColor: '#FFFFFF'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { boxWidth: 12, padding: 15, font: { weight: 600 } }
                        }
                    }
                }
            });
        }
    } catch (err) {
        console.error('Failed to load chart data:', err);
    }
}
