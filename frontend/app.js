/* ============================================
   CCPA Analyzer — Frontend Application
   ============================================ */

(() => {
    'use strict';

    // ---------- Configuration ----------
    const API_BASE_URL = 'http://localhost:8000';
    const ANALYZE_ENDPOINT = `${API_BASE_URL}/analyze`;
    const HEALTH_ENDPOINT = `${API_BASE_URL}/health`;
    const HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
    const SLOW_REQUEST_THRESHOLD = 10000; // 10 seconds

    // ---------- CCPA Section Explanations ----------
    const CCPA_SECTIONS = {
        '1798.100': {
            title: 'Right to Know',
            explanation: 'Consumers have the right to know what personal information is being collected about them, the sources, the business purpose, and the categories of third parties with whom it is shared.'
        },
        '1798.105': {
            title: 'Right to Delete',
            explanation: 'Consumers can request deletion of their personal information held by a business, and the business must comply and direct service providers to do the same.'
        },
        '1798.110': {
            title: 'Right to Know (Disclosure)',
            explanation: 'Businesses must disclose, upon request, the specific pieces of personal information they have collected about a consumer.'
        },
        '1798.115': {
            title: 'Right to Know (Categories)',
            explanation: 'Consumers can request the categories of personal information a business has sold or disclosed for a business purpose in the preceding 12 months.'
        },
        '1798.120': {
            title: 'Right to Opt-Out of Sale',
            explanation: 'Consumers have the right to direct a business that sells their personal information to stop selling that information. Special protections exist for minors under 16.'
        },
        '1798.125': {
            title: 'Non-Discrimination',
            explanation: 'Businesses cannot discriminate against consumers who exercise their CCPA rights — including by charging different prices, providing different quality, or denying services.'
        },
        '1798.130': {
            title: 'Notice Requirements',
            explanation: 'Businesses must make available specific methods for consumers to submit requests and respond to verified consumer requests within 45 days.'
        },
        '1798.135': {
            title: 'Opt-Out Link Requirement',
            explanation: 'Businesses must provide a clear and conspicuous "Do Not Sell My Personal Information" link on their website homepage.'
        },
        '1798.140': {
            title: 'Definitions',
            explanation: 'Defines key terms including "personal information," "consumer," "business," and "sell" as used throughout the CCPA statute.'
        },
        '1798.150': {
            title: 'Private Right of Action',
            explanation: 'Consumers whose unencrypted personal information is subject to unauthorized access can institute civil action for statutory damages between $100 and $750 per incident.'
        }
    };

    // ---------- DOM Elements ----------
    const elements = {
        statusIndicator: document.getElementById('status-indicator'),
        statusText: document.querySelector('.status-text'),
        promptInput: document.getElementById('prompt-input'),
        charCount: document.getElementById('char-count'),
        analyzeBtn: document.getElementById('analyze-btn'),
        inputError: document.getElementById('input-error'),
        loadingMessage: document.getElementById('loading-message'),
        loadingHint: document.getElementById('loading-hint'),
        resultsSection: document.getElementById('results-section'),
        resultPass: document.getElementById('result-pass'),
        resultFail: document.getElementById('result-fail'),
        violationsContainer: document.getElementById('violations-container'),
        exampleCards: document.querySelectorAll('.example-card')
    };

    // ---------- State ----------
    let isAnalyzing = false;
    let slowTimer = null;

    // ---------- Health Check ----------
    async function checkHealth() {
        const indicator = elements.statusIndicator;
        indicator.className = 'status-indicator status-checking';
        elements.statusText.textContent = 'Checking...';

        try {
            const response = await fetch(HEALTH_ENDPOINT, { 
                method: 'GET',
                signal: AbortSignal.timeout(5000)
            });
            if (response.ok) {
                indicator.className = 'status-indicator status-online';
                elements.statusText.textContent = 'Live';
            } else {
                throw new Error('Not OK');
            }
        } catch {
            indicator.className = 'status-indicator status-offline';
            elements.statusText.textContent = 'Offline';
        }
    }

    // ---------- Character Count ----------
    function updateCharCount() {
        const len = elements.promptInput.value.length;
        elements.charCount.textContent = `${len.toLocaleString()} character${len !== 1 ? 's' : ''}`;
    }

    // ---------- Show/Hide Error ----------
    function showError(message) {
        elements.inputError.textContent = message;
        elements.inputError.classList.remove('hidden');
    }

    function hideError() {
        elements.inputError.classList.add('hidden');
    }

    // ---------- Loading State ----------
    function setLoadingState(loading) {
        isAnalyzing = loading;
        const btn = elements.analyzeBtn;

        if (loading) {
            btn.classList.add('loading');
            btn.disabled = true;
            elements.loadingMessage.classList.remove('hidden');
            elements.loadingHint.classList.add('hidden');

            // Show slow request hint after threshold
            slowTimer = setTimeout(() => {
                elements.loadingHint.classList.remove('hidden');
            }, SLOW_REQUEST_THRESHOLD);
        } else {
            btn.classList.remove('loading');
            btn.disabled = false;
            elements.loadingMessage.classList.add('hidden');
            elements.loadingHint.classList.add('hidden');

            if (slowTimer) {
                clearTimeout(slowTimer);
                slowTimer = null;
            }
        }
    }

    // ---------- Parse Section Number ----------
    function parseSectionNumber(article) {
        // Handle formats: "Section 1798.120", "§1798.120", "1798.120", "Sec 1798.120"
        const match = article.match(/(\d{4}\.\d+)/);
        return match ? match[1] : null;
    }

    // ---------- Get Section Info ----------
    function getSectionInfo(article) {
        const sectionNum = parseSectionNumber(article);
        if (sectionNum && CCPA_SECTIONS[sectionNum]) {
            return {
                number: sectionNum,
                ...CCPA_SECTIONS[sectionNum]
            };
        }
        return {
            number: sectionNum || article,
            title: 'CCPA Provision',
            explanation: `This text may violate ${article} of the California Consumer Privacy Act.`
        };
    }

    // ---------- Render Results ----------
    function renderResults(data) {
        // Clear previous results
        elements.violationsContainer.innerHTML = '';

        // Show results section
        elements.resultsSection.classList.remove('hidden');

        if (data.harmful === false) {
            // PASS
            elements.resultPass.classList.remove('hidden');
            elements.resultFail.classList.add('hidden');
            elements.violationsContainer.classList.add('hidden');
        } else {
            // FAIL
            elements.resultPass.classList.add('hidden');
            elements.resultFail.classList.remove('hidden');
            elements.violationsContainer.classList.remove('hidden');

            // Render violation cards
            if (data.articles && data.articles.length > 0) {
                data.articles.forEach((article) => {
                    const info = getSectionInfo(article);
                    const card = document.createElement('div');
                    card.className = 'violation-card';
                    card.innerHTML = `
                        <div class="violation-section">§ ${info.number}</div>
                        <div class="violation-title">${info.title}</div>
                        <div class="violation-explanation">${info.explanation}</div>
                    `;
                    elements.violationsContainer.appendChild(card);
                });
            }
        }

        // Smooth scroll to results
        elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // ---------- Analyze Handler ----------
    async function handleAnalyze() {
        if (isAnalyzing) return;

        hideError();

        const text = elements.promptInput.value.trim();
        if (!text) {
            showError('Please paste some text to analyze. The input field cannot be empty.');
            elements.promptInput.focus();
            return;
        }

        // Hide previous results
        elements.resultsSection.classList.add('hidden');

        setLoadingState(true);

        try {
            const response = await fetch(ANALYZE_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text }),
                signal: AbortSignal.timeout(130000) // 130s (slightly over backend's 120s limit)
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Validate response structure
            if (typeof data.harmful !== 'boolean') {
                throw new Error('Invalid response: missing "harmful" field');
            }
            if (!Array.isArray(data.articles)) {
                throw new Error('Invalid response: missing "articles" field');
            }

            renderResults(data);

        } catch (error) {
            let message;
            if (error.name === 'TimeoutError' || error.name === 'AbortError') {
                message = 'Request timed out. The LLM inference took too long. Please try again.';
            } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                message = 'Cannot reach the backend server. Make sure it is running on port 8000.';
            } else {
                message = `Analysis failed: ${error.message}`;
            }
            showError(message);
        } finally {
            setLoadingState(false);
        }
    }

    // ---------- Example Card Handler ----------
    function handleExampleClick(event) {
        const card = event.currentTarget;
        const prompt = card.dataset.prompt;
        if (prompt) {
            elements.promptInput.value = prompt;
            updateCharCount();
            elements.promptInput.focus();
            hideError();

            // Hide previous results when loading new example
            elements.resultsSection.classList.add('hidden');
        }
    }

    // ---------- Initialize ----------
    function init() {
        // Character count
        elements.promptInput.addEventListener('input', updateCharCount);

        // Analyze button
        elements.analyzeBtn.addEventListener('click', handleAnalyze);

        // Allow Ctrl+Enter to submit
        elements.promptInput.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                handleAnalyze();
            }
        });

        // Example cards
        elements.exampleCards.forEach(card => {
            card.addEventListener('click', handleExampleClick);
        });

        // Initial health check
        checkHealth();

        // Periodic health check
        setInterval(checkHealth, HEALTH_CHECK_INTERVAL);

        // Initial char count
        updateCharCount();
    }

    // ---------- Start ----------
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
