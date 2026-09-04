import type { VideoMetadata } from './video'

export interface SavedVideoItem {
    video: VideoMetadata
    saved_at: string
}

export interface QueryHistoryItem {
    video_id: string
    query: string
    relevance_score: number | null
    answer: string | null
    created_at: string
}

export interface HistoryResponse {
    saved_videos: SavedVideoItem[]
    recent_queries: QueryHistoryItem[]
}