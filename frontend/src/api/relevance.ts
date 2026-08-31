import type { RelevanceResult } from '../types/relevance'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function fetchRelevance(videoId: string, query: string): Promise<RelevanceResult> {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/relevance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
    })

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}))
        throw new Error(errorBody.detail || `Request failed: ${response.status}`)
    }

    return response.json()
}