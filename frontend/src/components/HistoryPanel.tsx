import { useState } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { fetchHistory } from '../api/history'
import type { HistoryResponse } from '../types/history'

interface HistoryPanelProps {
    onSelectVideo: (youtubeUrl: string) => void
}

export function HistoryPanel({ onSelectVideo }: HistoryPanelProps) {
    const { getToken } = useAuth()
    const [open, setOpen] = useState(false)
    const [loading, setLoading] = useState(false)
    const [history, setHistory] = useState<HistoryResponse | null>(null)

    const handleToggle = async () => {
        const next = !open
        setOpen(next)
        if (next && !history) {
            setLoading(true)
            try {
                const token = await getToken()
                const result = await fetchHistory(token)
                setHistory(result)
            } catch {
                setHistory({ saved_videos: [], recent_queries: [] })
            } finally {
                setLoading(false)
            }
        }
    }

    return (
        <div className="mb-4">
            <button
                onClick={handleToggle}
                className="text-sm text-slate-600 hover:text-slate-900 underline underline-offset-2"
            >
                {open ? 'Hide history' : 'View history'}
            </button>

            {open && (
                <div className="mt-3 text-left bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
                    {loading && <p className="text-sm text-slate-400">Loading history...</p>}

                    {!loading && history && (
                        <>
                            <div>
                                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                                    Saved videos
                                </h4>
                                {history.saved_videos.length === 0 && (
                                    <p className="text-sm text-slate-400">No saved videos yet.</p>
                                )}
                                <ul className="space-y-2">
                                    {history.saved_videos.map((item) => (
                                        <li key={item.video.video_id}>
                                            <button
                                                onClick={() =>
                                                    onSelectVideo(`https://www.youtube.com/watch?v=${item.video.video_id}`)
                                                }
                                                className="text-sm text-slate-800 hover:text-slate-950 text-left underline underline-offset-2"
                                            >
                                                {item.video.title}
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div>
                                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                                    Recent questions
                                </h4>
                                {history.recent_queries.length === 0 && (
                                    <p className="text-sm text-slate-400">No questions asked yet.</p>
                                )}
                                <ul className="space-y-2">
                                    {history.recent_queries.map((q, i) => (
                                        <li key={i} className="text-sm text-slate-700">
                                            <span className="font-medium">{q.query}</span>
                                            {q.answer && <p className="text-slate-500 mt-0.5">{q.answer}</p>}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </>
                    )}
                </div>
            )}
        </div>
    )
}