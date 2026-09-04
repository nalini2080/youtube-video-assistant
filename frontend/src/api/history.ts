import type { HistoryResponse } from '../types/history'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function authHeaders(token: string | null): HeadersInit {
    return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function saveVideo(videoId: string, token: string | null): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/save`, {
        method: 'POST',
        headers: authHeaders(token),
    })
    if (!response.ok) throw new Error('Failed to save video.')
}

export async function unsaveVideo(videoId: string, token: string | null): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/save`, {
        method: 'DELETE',
        headers: authHeaders(token),
    })
    if (!response.ok) throw new Error('Failed to unsave video.')
}

export async function fetchHistory(token: string | null): Promise<HistoryResponse> {
    const response = await fetch(`${API_BASE_URL}/api/videos/history`, {
        headers: authHeaders(token),
    })
    if (!response.ok) throw new Error('Failed to load history.')
    return response.json()
}