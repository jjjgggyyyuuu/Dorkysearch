// DorkySearch API Client

import { fetchWithTimeout } from './utils.js';

class ApiClient {
    constructor(baseUrl = '/api.php') {
        this.baseUrl = baseUrl;
        this.defaultTimeout = 30000; // 30 seconds
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const { timeout = this.defaultTimeout, ...fetchOptions } = options;
        
        try {
            const response = await fetchWithTimeout(`${this.baseUrl}${endpoint}`, {
                ...fetchOptions,
                headers: {
                    'Content-Type': 'application/json',
                    ...fetchOptions.headers,
                },
                timeout,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Domain analysis methods
    async analyzeDomain(domain) {
        return this.request('', {
            method: 'POST',
            body: JSON.stringify({ domain }),
        });
    }

    async batchAnalyzeDomains(domains) {
        return this.request('/batch', {
            method: 'POST',
            body: JSON.stringify({ domains }),
        });
    }

    // Search history methods
    async getSearchHistory(page = 1, limit = 10) {
        return this.request(`/history?page=${page}&limit=${limit}`);
    }

    async clearSearchHistory() {
        return this.request('/history', {
            method: 'DELETE',
        });
    }

    // Saved domains methods
    async getSavedDomains() {
        return this.request('/saved');
    }

    async saveDomain(domain, notes = '') {
        return this.request('/saved', {
            method: 'POST',
            body: JSON.stringify({ domain, notes }),
        });
    }

    async removeSavedDomain(domain) {
        return this.request('/saved', {
            method: 'DELETE',
            body: JSON.stringify({ domain }),
        });
    }

    // Domain suggestions
    async getDomainSuggestions(keyword) {
        return this.request(`/suggestions?keyword=${encodeURIComponent(keyword)}`);
    }

    // Domain value estimation
    async estimateDomainValue(domain) {
        return this.request('/estimate', {
            method: 'POST',
            body: JSON.stringify({ domain }),
        });
    }

    // WHOIS lookup
    async getWhoisInfo(domain) {
        return this.request(`/whois?domain=${encodeURIComponent(domain)}`);
    }

    // DNS records
    async getDnsRecords(domain) {
        return this.request(`/dns?domain=${encodeURIComponent(domain)}`);
    }

    // Domain availability check
    async checkDomainAvailability(domain) {
        return this.request(`/available?domain=${encodeURIComponent(domain)}`);
    }

    // Bulk operations
    async bulkCheckAvailability(domains) {
        return this.request('/bulk-check', {
            method: 'POST',
            body: JSON.stringify({ domains }),
        });
    }

    // Domain monitoring
    async addDomainMonitor(domain, options = {}) {
        return this.request('/monitor', {
            method: 'POST',
            body: JSON.stringify({ domain, ...options }),
        });
    }

    async removeDomainMonitor(domain) {
        return this.request('/monitor', {
            method: 'DELETE',
            body: JSON.stringify({ domain }),
        });
    }

    async getMonitoredDomains() {
        return this.request('/monitor');
    }

    // Error handling
    handleError(error) {
        if (error.name === 'AbortError') {
            return {
                error: true,
                message: 'Request timed out. Please try again.',
                code: 'TIMEOUT',
            };
        }

        if (error.response) {
            return {
                error: true,
                message: error.response.data.message || 'An error occurred',
                code: error.response.status,
            };
        }

        return {
            error: true,
            message: 'Network error. Please check your connection.',
            code: 'NETWORK_ERROR',
        };
    }
}

// Create and export a singleton instance
const apiClient = new ApiClient();
export default apiClient;

// Also export the class for testing or custom initialization
export { ApiClient }; 