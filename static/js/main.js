document.addEventListener('DOMContentLoaded', function() {
    // Animate elements with fade-in class
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Handle search form submission
    const searchForm = document.querySelector('form[action="/search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const queryInput = document.getElementById('query');
            if (!queryInput.value.trim()) {
                e.preventDefault();
                alert('Please enter a search query');
                queryInput.focus();
            } else {
                // Show loading indicator
                const submitBtn = this.querySelector('button[type="submit"]');
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Searching...';
                submitBtn.disabled = true;
            }
        });
    }
    
    // Handle search type selection
    const searchTypeInputs = document.querySelectorAll('input[name="type"]');
    searchTypeInputs.forEach(input => {
        input.addEventListener('change', function() {
            const queryInput = document.getElementById('query');
            const placeholderMap = {
                'general': 'Enter your search query',
                'documents': 'Search for documents, PDFs, spreadsheets...',
                'sensitive': 'Search for potentially sensitive information...',
                'directories': 'Search for exposed directories...',
                'technology': 'Search for specific technologies or platforms...',
                'phone': 'Enter a phone number to analyze...'
            };
            
            queryInput.placeholder = placeholderMap[this.value] || 'Enter your search query';
            
            // Update query input type for phone numbers
            if (this.value === 'phone') {
                queryInput.type = 'tel';
                queryInput.pattern = '[0-9+\\-\\s()]*';
            } else {
                queryInput.type = 'text';
                queryInput.removeAttribute('pattern');
            }
        });
    });
    
    // Initialize search history display
    displaySearchHistory();
    
    // Clear search history button
    const clearHistoryBtn = document.getElementById('clear-history');
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', function() {
            localStorage.removeItem('searchHistory');
            displaySearchHistory();
        });
    }
});

// Utility Functions

function getSelectedSearchType() {
    const selectedInput = document.querySelector('input[name="type"]:checked');
    return selectedInput ? selectedInput.value : 'general';
}

function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const searchCard = document.querySelector('.search-card');
    if (searchCard) {
        searchCard.parentNode.insertBefore(alertContainer, searchCard);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertContainer.classList.remove('show');
            setTimeout(() => alertContainer.remove(), 300);
        }, 5000);
    }
}

// Search History Functions

function saveSearchHistory(query, type) {
    const searchHistory = getSearchHistory();
    
    // Add new search to the beginning
    searchHistory.unshift({
        query: query,
        type: type,
        timestamp: new Date().toISOString()
    });
    
    // Keep only the most recent 10 searches
    const updatedHistory = searchHistory.slice(0, 10);
    
    // Save to localStorage
    localStorage.setItem('searchHistory', JSON.stringify(updatedHistory));
}

function getSearchHistory() {
    const history = localStorage.getItem('searchHistory');
    return history ? JSON.parse(history) : [];
}

function displaySearchHistory() {
    const historyContainer = document.getElementById('search-history');
    if (!historyContainer) return;
    
    const history = getSearchHistory();
    
    if (history.length === 0) {
        historyContainer.innerHTML = '<p class="text-muted">No search history yet</p>';
        return;
    }
    
    const historyHTML = history.map((item, index) => {
        const date = new Date(item.timestamp);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        const typeIcon = getSearchTypeIcon(item.type);
        
        return `
            <div class="search-history-item">
                <div class="d-flex justify-content-between align-items-center">
                    <span>
                        <i class="${typeIcon} me-2"></i>
                        <a href="#" class="history-query-link" data-query="${item.query}" data-type="${item.type}">${item.query}</a>
                    </span>
                    <small class="text-muted">${formattedDate}</small>
                </div>
            </div>
        `;
    }).join('');
    
    historyContainer.innerHTML = historyHTML;
    
    // Add event listeners to history links
    document.querySelectorAll('.history-query-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const query = this.dataset.query;
            const type = this.dataset.type;
            
            // Set form values
            document.getElementById('query').value = query;
            document.querySelector(`input[name="type"][value="${type}"]`).checked = true;
            
            // Trigger form submission
            document.querySelector('form[action="/search"]').submit();
        });
    });
}

function getSearchTypeIcon(type) {
    const iconMap = {
        'general': 'fas fa-globe',
        'documents': 'fas fa-file',
        'sensitive': 'fas fa-user-shield',
        'directories': 'fas fa-folder',
        'technology': 'fas fa-code',
        'phone': 'fas fa-phone'
    };
    
    return iconMap[type] || 'fas fa-search';
} 