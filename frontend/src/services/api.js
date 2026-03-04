const BASE_URL = 'http://localhost:8000';

/**
 * Check backend health status.
 */
export async function checkHealth() {
    const response = await fetch(`${BASE_URL}/health`);
    if (!response.ok) throw new Error('Backend offline');
    return response.json();
}

/**
 * Analyze a policy by sending to /analyze.
 * Returns the full JSON response (non-streaming).
 */
export async function analyzePolicy(prompt) {
    const response = await fetch(`${BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'sam'
        },
        body: JSON.stringify({ prompt }),
    });
    if (!response.ok) throw new Error('Analysis failed');
    return response.json();
}

/**
 * Analyze a policy with STREAMING support.
 * Calls /analyze and simulates streaming the explanation field for the UI.
 * 
 * @param {string} prompt - The user's business practice text
 * @param {function} onChunk - Called with each text chunk as it arrives
 * @param {function} onDone - Called with the final parsed JSON response when streaming completes
 */
export async function analyzePolicyStream(prompt, onChunk, onDone) {
    const response = await fetch(`${BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'sam'
        },
        body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
        throw new Error('Analysis failed with status: ' + response.status);
    }

    const result = await response.json();

    // Simulate streaming by typing out the explanation text
    const text = result.explanation || "Analysis complete.";
    for (let i = 0; i < text.length; i += 3) {
        onChunk(text.slice(i, i + 3));
        await new Promise(resolve => setTimeout(resolve, 15));
    }

    onDone(result);
}

