// DorkySearch Main JavaScript

// DOM Elements
const searchForm = document.getElementById('searchForm');
const domainInput = document.getElementById('domainInput');
const resultsSection = document.getElementById('resultsSection');
const loadingSpinner = document.getElementById('loadingSpinner');

// Configuration
const API_URL = '/api.php';
const DEBOUNCE_DELAY = 300;

// Utility Functions
const debounce = (func, delay) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(null, args), delay);
    };
};

const showLoading = () => {
    loadingSpinner.classList.remove('hidden');
};

const hideLoading = () => {
    loadingSpinner.classList.add('hidden');
};

const showAlert = (message, type = 'error') => {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.textContent = message;
    resultsSection.prepend(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
};

// Domain Analysis Functions
const analyzeDomain = async (domain) => {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
};

const displayResults = (results) => {
    const resultCard = document.createElement('div');
    resultCard.className = 'result-card fade-in';

    const valueScore = results.value_score.score;
    const scoreClass = valueScore >= 70 ? 'text-success' :
                      valueScore >= 50 ? 'text-warning' : 'text-error';

    resultCard.innerHTML = `
        <h3 class="result-title">${results.domain}</h3>
        <div class="result-meta">
            <span class="domain-status ${results.available ? 'text-success' : 'text-error'}">
                ${results.available ? 'Available' : 'Taken'}
            </span>
            <span class="domain-score ${scoreClass}">
                Value Score: ${valueScore}/100
            </span>
        </div>
        <div class="result-content">
            <h4>Domain Analysis</h4>
            <ul>
                ${Object.entries(results.value_score.factors)
                    .map(([key, value]) => `<li>${key}: ${value}</li>`)
                    .join('')}
            </ul>
            
            <h4>SEO Metrics</h4>
            <ul>
                ${Object.entries(results.seo_metrics)
                    .map(([key, value]) => `<li>${key.replace('_', ' ')}: ${value}</li>`)
                    .join('')}
            </ul>

            <h4>Similar Domains</h4>
            <ul class="suggestions-list">
                ${results.suggestions
                    .map(suggestion => `<li>${suggestion}</li>`)
                    .join('')}
            </ul>
        </div>
    `;

    resultsSection.prepend(resultCard);
};

// Event Listeners
searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const domain = domainInput.value.trim();

    if (!domain) {
        showAlert('Please enter a domain name');
        return;
    }

    showLoading();
    try {
        const results = await analyzeDomain(domain);
        hideLoading();
        displayResults(results);
    } catch (error) {
        hideLoading();
        showAlert('Error analyzing domain. Please try again.');
    }
});

// Real-time validation
domainInput.addEventListener('input', debounce((e) => {
    const domain = e.target.value.trim();
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/;
    
    if (domain && !domainRegex.test(domain)) {
        domainInput.classList.add('error');
        showAlert('Please enter a valid domain name');
    } else {
        domainInput.classList.remove('error');
    }
}, DEBOUNCE_DELAY));

// Dark mode toggle
const darkModeToggle = document.getElementById('darkModeToggle');
if (darkModeToggle) {
    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
    });

    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
}

// Initialize tooltips
const initTooltips = () => {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = e.target.dataset.tooltip;
            document.body.appendChild(tooltip);

            const rect = e.target.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
            tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
        });

        element.addEventListener('mouseleave', () => {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initTooltips();
}); 