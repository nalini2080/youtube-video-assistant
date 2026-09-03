import type { RelevanceResult } from '../types/relevance'
import { TimestampChip } from './TimestampChip'
import { parseTimestampToSeconds } from '../utils/timestamps'

interface RelevanceCardProps {
    loading: boolean
    error: string | null
    relevance: RelevanceResult | null
    videoId: string
}

export function RelevanceCard({ loading, error, relevance, videoId }: RelevanceCardProps) {
    if (loading) {
        return (
            <div className="text-left bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <div className="space-y-3 animate-pulse">
                    <div className="h-8 bg-slate-100 rounded w-1/2 mx-auto" />
                    <div className="h-6 bg-slate-100 rounded w-1/3 mx-auto" />
                    <div className="h-3 bg-slate-100 rounded w-full mt-4" />
                    <div className="h-3 bg-slate-100 rounded w-2/3" />
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="text-left bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <h3 className="text-sm font-semibold text-slate-900 mb-1">Relevance to Your Goal</h3>
                <p className="text-sm text-red-600">{error}</p>
            </div>
        )
    }

    if (!relevance) return null

    const isRelevant = relevance.relevant
    const scorePercent = Math.round(relevance.score * 100)

    return (
        <div
            className={`rounded-2xl p-6 border-2 shadow-sm ${isRelevant ? 'bg-green-50 border-green-200' : 'bg-amber-50 border-amber-200'
                }`}
        >
            <div className="text-center">
                <p
                    className={`text-5xl font-bold tracking-tight ${isRelevant ? 'text-green-700' : 'text-amber-700'
                        }`}
                >
                    {scorePercent}%
                </p>
                <p className={`text-xs font-medium mt-1 ${isRelevant ? 'text-green-600' : 'text-amber-600'}`}>
                    relevant to your goal
                </p>

                <div
                    className={`inline-flex items-center gap-2 mt-4 px-4 py-2 rounded-full text-sm font-semibold ${isRelevant ? 'bg-green-600 text-white' : 'bg-amber-500 text-white'
                        }`}
                >
                    {isRelevant ? '✓ YES — WATCH THIS' : '⚠ PROBABLY NOT A FIT'}
                </div>

                <p className="text-sm text-slate-700 mt-4 max-w-md mx-auto">{relevance.reason}</p>
            </div>

            {(relevance.covered_topics.length > 0 || relevance.missing_topics.length > 0) && (
                <div className="grid sm:grid-cols-2 gap-4 mt-6 pt-5 border-t border-black/5">
                    {relevance.covered_topics.length > 0 && (
                        <div>
                            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                                This video covers
                            </h4>
                            <ul className="space-y-1">
                                {relevance.covered_topics.map((topic, i) => (
                                    <li key={i} className="text-sm text-slate-800 flex items-start gap-2">
                                        <span className="text-green-600 shrink-0">✓</span>
                                        <span>{topic}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {relevance.missing_topics.length > 0 && (
                        <div>
                            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                                It does NOT cover
                            </h4>
                            <ul className="space-y-1">
                                {relevance.missing_topics.map((topic, i) => (
                                    <li key={i} className="text-sm text-slate-800 flex items-start gap-2">
                                        <span className="text-amber-500 shrink-0">⚠</span>
                                        <span>{topic}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {relevance.relevant_timestamps.length > 0 && (
                <div className="mt-5 pt-5 border-t border-black/5 text-center">
                    <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                        Most relevant {relevance.relevant_timestamps.length > 1 ? 'sections' : 'section'}
                    </h4>
                    <div className="flex flex-wrap justify-center gap-2">
                        {relevance.relevant_timestamps.map((ts, i) => {
                            const seconds = parseTimestampToSeconds(ts)
                            return seconds !== null ? (
                                <TimestampChip key={i} videoId={videoId} seconds={seconds} label={ts} />
                            ) : (
                                <span key={i} className="text-xs font-mono bg-slate-200 text-slate-500 px-2 py-1 rounded">
                                    {ts}
                                </span>
                            )
                        })}
                    </div>
                </div>
            )}
        </div>
    )
}