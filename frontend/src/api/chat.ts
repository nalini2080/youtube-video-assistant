import type { ChatResponse } from '../types/chat'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function sendChatMessage(videoId: string, message: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
    })

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}))
        throw new Error(errorBody.detail || `Request failed: ${response.status}`)
    }

    return response.json()
}