// Chart initialization and configuration functions

const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                padding: 20,
                usePointStyle: true,
                font: {
                    family: "'Inter', sans-serif"
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(31, 41, 55, 0.9)',
            padding: 12,
            titleFont: { size: 14, family: "'Inter', sans-serif" },
            bodyFont: { size: 13, family: "'Inter', sans-serif" },
            cornerRadius: 8,
            displayColors: true
        }
    }
};

const CHART_COLORS = [
    '#3B82F6', // Blue
    '#EF4444', // Red
    '#10B981', // Green
    '#F59E0B', // Yellow
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#14B8A6', // Teal
    '#F97316', // Orange
    '#6366F1', // Indigo
    '#64748B'  // Slate
];

function formatCurrency(amount) {
    if (amount === undefined || amount === null) return '₹0';
    return '₹' + amount.toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

function initCategoryPieChart(canvasId, categoryData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !categoryData || categoryData.length === 0) return null;

    const labels = categoryData.map(item => item.category);
    const data = categoryData.map(item => item.total);

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: CHART_COLORS.slice(0, data.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            ...commonOptions,
            cutout: '65%',
            plugins: {
                ...commonOptions.plugins,
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += formatCurrency(context.parsed);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function initMonthlyBarChart(canvasId, monthlyData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !monthlyData || monthlyData.length === 0) return null;

    const labels = monthlyData.map(item => item.month_name ? (item.month_name + (item.year ? ' ' + item.year : '')) : ('Month ' + item.month));
    const data = monthlyData.map(item => item.total !== undefined ? item.total : (item.amount || 0));

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Expenses',
                data: data,
                backgroundColor: '#3B82F6',
                borderRadius: 4,
                barThickness: 'flex',
                maxBarThickness: 40
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                legend: { display: false },
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { borderDash: [2, 4], color: '#e5e7eb' },
                    ticks: {
                        callback: function(value) { return formatCurrency(value); }
                    }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function initTrendLineChart(canvasId, trendData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !trendData || trendData.length === 0) return null;

    const labels = trendData.map(item => item.month_name ? (item.month_name + (item.year ? ' ' + item.year : '')) : ('Month ' + (item.month || '')));
    const incomeData = trendData.map(item => item.income || 0);
    const expenseData = trendData.map(item => item.expenses !== undefined ? item.expenses : (item.expense || 0));

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Income',
                    data: incomeData,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#10B981'
                },
                {
                    label: 'Expenses',
                    data: expenseData,
                    borderColor: '#EF4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#EF4444'
                }
            ]
        },
        options: {
            ...commonOptions,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { borderDash: [2, 4], color: '#e5e7eb' },
                    ticks: {
                        callback: function(value) { return formatCurrency(value); }
                    }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function initCategoryBarChart(canvasId, categoryData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !categoryData || categoryData.length === 0) return null;

    // Sort descending
    const sortedData = [...categoryData].sort((a, b) => b.total - a.total);
    
    const labels = sortedData.map(item => item.category);
    const data = sortedData.map(item => item.total);

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Amount spent',
                data: data,
                backgroundColor: CHART_COLORS.slice(0, data.length),
                borderRadius: 4
            }]
        },
        options: {
            ...commonOptions,
            indexAxis: 'y',
            plugins: {
                ...commonOptions.plugins,
                legend: { display: false },
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return formatCurrency(context.parsed.x);
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { borderDash: [2, 4], color: '#e5e7eb' },
                    ticks: {
                        callback: function(value) { return formatCurrency(value); }
                    }
                },
                y: {
                    grid: { display: false }
                }
            }
        }
    });
}
