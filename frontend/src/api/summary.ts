import type { VideoSummary } from '../types/summary'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function fetchSummary(videoId: string): Promise<VideoSummary> {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/summary`, {
        method: 'POST',
    })

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}))
        throw new Error(errorBody.detail || `Request failed: ${response.status}`)
    }

    return response.json()
}