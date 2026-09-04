export interface SuggestedVideo {
    video_id: string
    title: string
    channel: string
    thumbnail_url: string
    topic: string
}

export interface SuggestionsResponse {
    suggestions: SuggestedVideo[]
    quota_exceeded: boolean
}