export interface RelevanceResult {
    video_id: string
    relevant: boolean
    score: number
    reason: string
    covered_topics: string[]
    missing_topics: string[]
    relevant_timestamps: string[]
}