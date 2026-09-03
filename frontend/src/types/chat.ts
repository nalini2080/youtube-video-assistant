export interface ChatSource {
    text: string
    start_time: number
    end_time: number
}

export interface ChatResponse {
    video_id: string
    answer: string
    sources: ChatSource[]
    timestamps: string[]
}