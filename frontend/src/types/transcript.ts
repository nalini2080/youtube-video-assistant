export interface TranscriptSnippet {
    text: string
    start: number
    duration: number
}

export interface TranscriptResponse {
    video_id: string
    available: boolean
    language: string | null
    language_code: string | null
    is_generated: boolean | null
    snippets: TranscriptSnippet[]
    reason: string | null
}