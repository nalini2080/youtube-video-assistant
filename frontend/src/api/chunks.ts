import type { TranscriptChunk } from '../types/chunk'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function fetchChunks(videoId: string): Promise<TranscriptChunk[]> {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/chunks`)

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}))
        throw new Error(errorBody.detail || `Request failed: ${response.status}`)
    }

    return response.json()
}