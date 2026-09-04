import type { SuggestionsResponse } from '../types/suggestion'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function fetchSuggestions(
    videoId: string,
    topics: string[]
): Promise<SuggestionsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topics }),
    })

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}))
        throw new Error(errorBody.detail || `Request failed: ${response.status}`)
    }

    return response.json()
}