export function parseTimestampToSeconds(timestamp: string): number | null {
    const match = timestamp.trim().match(/^(\d+):(\d{1,2})$/)
    if (!match) return null

    const minutes = parseInt(match[1], 10)
    const seconds = parseInt(match[2], 10)
    if (seconds >= 60) return null

    return minutes * 60 + seconds
}

export function formatTimestamp(seconds: number): string {
    const minutes = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${minutes}:${secs.toString().padStart(2, '0')}`
}

export function youtubeTimestampUrl(videoId: string, seconds: number): string {
    return `https://www.youtube.com/watch?v=${videoId}&t=${Math.floor(seconds)}s`
}