import type { PersonalizedSummaryResult } from '../types/personalizedSummary'
import { TimestampChip } from './TimestampChip'
import { parseTimestampToSeconds } from '../utils/timestamps'

interface PersonalizedSummaryCardProps {
    loading: boolean
    error: string | null
    personalizedSummary: PersonalizedSummaryResult | null
    videoId: string
}

export function PersonalizedSummaryCard({
    loading,
    error,
    personalizedSummary,
    videoId,
}: PersonalizedSummaryCardProps) {
    return (
        <div className="text-left bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">For Your Goal</h3>

            {loading && (
                <div className="space-y-2 animate-pulse">
                    <div className="h-3 bg-slate-100 rounded w-full" />
                    <div className="h-3 bg-slate-100 rounded w-5/6" />
                </div>
            )}

            {error && <p className="text-sm text-red-600">{error}</p>}

            {!loading && personalizedSummary && (
                <div className="space-y-4">
                    <p className="text-sm text-slate-700">{personalizedSummary.summary}</p>

                    {personalizedSummary.relevant_points.length > 0 && (
                        <div>
                            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                                Relevant Points
                            </h4>
                            <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                                {personalizedSummary.relevant_points.map((point, i) => (
                                    <li key={i}>{point}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {personalizedSummary.timestamps.length > 0 && (
                        <div>
                            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                                Jump To
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {personalizedSummary.timestamps.map((ts, i) => {
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
            )}
        </div>
    )
}