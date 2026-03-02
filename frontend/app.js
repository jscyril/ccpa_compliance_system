/**
 * CCPA Compliance Analyzer - Minimalist Enterprise Frontend
 */

document.addEventListener('DOMContentLoaded', () => {
    // ---------- Config & Elements ----------
    const API_URL = 'http://localhost:8000/analyze';
    const HEALTH_URL = 'http://localhost:8000/health';

    const elements = {
        promptInput: document.getElementById('prompt-input'),
        analyzeBtn: document.getElementById('analyze-btn'),
        btnText: document.querySelector('.btn-text'),
        emptyState: document.getElementById('empty-state'),
        resultsContainer: document.getElementById('results-container'),
        verdictCard: document.getElementById('verdict-card'),
        verdictIcon: document.getElementById('verdict-icon'),
        verdictStatus: document.getElementById('verdict-status'),
        jsonOutput: document.getElementById('json-output'),
        btnCopyJson: document.getElementById('btn-copy-json'),
        statusIndicator: document.getElementById('status-indicator'),
        statusDot: document.getElementById('status-dot'),
        statusText: document.querySelector('.status-text'),
        toastContainer: document.getElementById('toast-container'),
    };

    let currentJsonData = null;

    // ---------- Health Check ----------
    async function checkHealth() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);

            const response = await fetch(HEALTH_URL, {
                method: 'GET',
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                elements.statusText.textContent = 'Status: Online';
                elements.statusDot.classList.remove('offline');
                elements.statusDot.classList.add('online');
            } else {
                throw new Error('Server not OK');
            }
        } catch (err) {
            elements.statusText.textContent = 'Status: Offline';
            elements.statusDot.classList.remove('online');
            elements.statusDot.classList.add('offline');
        }
    }

    setInterval(checkHealth, 30000);
    checkHealth(); // Initial check

    // ---------- Toast Notifications ----------
    function showToast(message, isError = false) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        if (isError) {
            toast.style.backgroundColor = 'var(--verdict-fail)';
            toast.style.color = '#fff';
        }

        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // ---------- Syntax Highlighting ----------
    function syntaxHighlight(jsonStr) {
        if (!jsonStr) return "";
        jsonStr = jsonStr.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

        return jsonStr.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            let cls = 'json-number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'json-key';
                } else {
                    cls = 'json-string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'json-boolean';
            } else if (/null/.test(match)) {
                cls = 'json-null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }

    // ---------- Rendering ----------
    function renderResults(data) {
        currentJsonData = data;

        // Hide empty state, show results
        elements.emptyState.classList.add('hidden');
        elements.resultsContainer.classList.remove('hidden');

        // Update Verdict Card
        elements.verdictCard.className = 'verdict-card'; // reset
        elements.verdictIcon.innerHTML = '';

        if (data.harmful === false) {
            // PASS
            elements.verdictCard.classList.add('pass');
            elements.verdictStatus.textContent = 'Compliant';
            elements.verdictStatus.style.color = 'var(--verdict-pass)';
            elements.verdictIcon.innerHTML = `
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--verdict-pass)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        `;
        } else {
            // FAIL / FLAG
            elements.verdictCard.classList.add('fail');
            elements.verdictStatus.textContent = 'Review Required';
            elements.verdictStatus.style.color = 'var(--verdict-fail)';
            elements.verdictIcon.innerHTML = `
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--verdict-fail)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        `;
        }

        // Render JSON
        const formattedJson = JSON.stringify(data, null, 2);
        elements.jsonOutput.innerHTML = `<code>${syntaxHighlight(formattedJson)}</code>`;
    }

    function setLoading(isLoading) {
        if (isLoading) {
            elements.analyzeBtn.disabled = true;
            elements.btnText.innerHTML = '<div class="spinner"></div> Analyzing...';
        } else {
            elements.analyzeBtn.disabled = false;
            elements.btnText.textContent = 'Run Analysis';
        }
    }

    // ---------- Actions ----------
    async function handleAnalyze() {
        const text = elements.promptInput.value.trim();
        if (!text) {
            showToast('Please enter a policy to analyze.', true);
            elements.promptInput.focus();
            return;
        }

        setLoading(true);
        elements.emptyState.classList.add('hidden');

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text })
            });

            if (!response.ok) throw new Error('Network error or server unavailable');

            const data = await response.json();
            renderResults(data);

        } catch (error) {
            showToast('Analysis failed: ' + error.message, true);
            elements.emptyState.classList.remove('hidden');
            elements.resultsContainer.classList.add('hidden');
        } finally {
            setLoading(false);
        }
    }

    function handleCopyJson() {
        if (!currentJsonData) return;
        navigator.clipboard.writeText(JSON.stringify(currentJsonData, null, 2))
            .then(() => showToast('JSON copied to clipboard'))
            .catch(() => showToast('Failed to copy', true));
    }

    // ---------- Event Listeners ----------
    elements.analyzeBtn.addEventListener('click', handleAnalyze);
    elements.btnCopyJson.addEventListener('click', handleCopyJson);

    // Command+Enter / Ctrl+Enter shortcut
    elements.promptInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            handleAnalyze();
        }
    });
});
