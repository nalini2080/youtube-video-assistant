import type { RelevanceResult } from '../types/relevance'

interface RelevanceCardProps {
    loading: boolean
    error: string | null
    relevance: RelevanceResult | null
}

export function RelevanceCard({ loading, error, relevance }: RelevanceCardProps) {
    return (
        <div className="text-left bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">Relevance to Your Goal</h3>

            {loading && (
                <div className="space-y-2 animate-pulse">
                    <div className="h-3 bg-slate-100 rounded w-1/3" />
                    <div className="h-3 bg-slate-100 rounded w-full" />
                    <div className="h-3 bg-slate-100 rounded w-2/3" />
                </div>
            )}

            {error && <p className="text-sm text-red-600">{error}</p>}

            {!loading && relevance && (
                <div className="space-y-4">
                    <div className="flex items-center gap-3">
                        <span
                            className={`text-xs font-semibold px-3 py-1 rounded-full ${relevance.relevant
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-amber-100 text-amber-800'
                                }`}
                        >
                            {relevance.relevant ? 'YES — Watch this' : 'Probably not a fit'}
                        </span>
                        <span className="text-sm text-slate-500">
                            {Math.round(relevance.score * 100)}% relevant
                        </span>
                    </div>

                    <p className="text-sm text-slate-700">{relevance.reason}</p>

                    {relevance.covered_topics.length > 0 && (
                        <div>
                            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                                Covers
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {relevance.covered_topics.map((topic, i) => (
                                    <span key={i} className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full">
                                        ✓ {topic}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {relevance.missing_topics.length > 0 && (
                        <div>
                            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                                Does NOT cover
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {relevance.missing_topics.map((topic, i) => (
                                    <span key={i} className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full">
                                        ⚠ {topic}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {relevance.relevant_timestamps.length > 0 && (
                        <div>
                            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                                Most Relevant Sections
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {relevance.relevant_timestamps.map((ts, i) => (
                                    <span key={i} className="text-xs font-mono bg-slate-900 text-white px-2 py-1 rounded">
                                        {ts}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}