import type { VideoMetadata } from '../types/video'

function formatDuration(totalSeconds: number): string {
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60
    if (hours > 0) return `${hours}h ${minutes}m`
    if (minutes > 0) return `${minutes}m ${seconds}s`
    return `${seconds}s`
}

interface VideoMetadataCardProps {
    video: VideoMetadata
}

export function VideoMetadataCard({ video }: VideoMetadataCardProps) {
    return (
        <div className="text-left bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
            <img src={video.thumbnail_url} alt={video.title} className="w-full" />
            <div className="p-5">
                <h2 className="text-lg font-semibold text-slate-900">{video.title}</h2>
                <p className="text-sm text-slate-500 mt-1">
                    {video.channel} • {formatDuration(video.duration_seconds)}
                </p>
                <p className="text-sm text-slate-700 mt-3 line-clamp-4">
                    {video.description}
                </p>
            </div>
        </div>
    )
}