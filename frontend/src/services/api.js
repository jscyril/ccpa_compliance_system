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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
    });
    if (!response.ok) throw new Error('Analysis failed');
    return response.json();
}

/**
 * Analyze a policy with STREAMING support.
 * Calls /analyze/stream (SSE) if available; falls back to /analyze.
 * 
 * @param {string} prompt - The user's business practice text
 * @param {function} onChunk - Called with each text chunk as it arrives
 * @param {function} onDone - Called with the final parsed JSON response when streaming completes
 */
export async function analyzePolicyStream(prompt, onChunk, onDone) {
    const response = await fetch(`${BASE_URL}/analyze/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
    });

    // If streaming endpoint not available, fall back to regular analyze
    if (!response.ok) {
        const fallback = await analyzePolicy(prompt);
        // Simulate streaming by feeding chunks of the stringified result
        const text = JSON.stringify(fallback, null, 2);
        for (let i = 0; i < text.length; i += 3) {
            onChunk(text.slice(i, i + 3));
            await new Promise(resolve => setTimeout(resolve, 10));
        }
        onDone(fallback);
        return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let finalResult = null;

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        // Parse SSE lines: "data: {...}\n\n"
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? ''; // keep incomplete line in buffer

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6).trim();
                if (data === '[DONE]') {
                    if (finalResult) onDone(finalResult);
                    return;
                }
                try {
                    const parsed = JSON.parse(data);
                    if (parsed.chunk !== undefined) {
                        // Streaming text chunk
                        onChunk(parsed.chunk);
                    } else if (parsed.harmful !== undefined) {
                        // Final result object
                        finalResult = parsed;
                        onDone(finalResult);
                    }
                } catch {
                    // Plain text chunk (non-JSON streaming)
                    onChunk(data);
                }
            }
        }
    }

    // If stream ended without [DONE], try parsing buffer as final result
    if (buffer.trim()) {
        try {
            const parsed = JSON.parse(buffer);
            if (parsed.harmful !== undefined) onDone(parsed);
        } catch { /* ignore */ }
    }
}
