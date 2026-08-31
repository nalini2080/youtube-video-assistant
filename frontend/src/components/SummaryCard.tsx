import type { VideoSummary } from '../types/summary'

interface SummaryCardProps {
    loading: boolean
    error: string | null
    summary: VideoSummary | null
}

export function SummaryCard({ loading, error, summary }: SummaryCardProps) {
    return (
        <div className="text-left bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">AI Summary</h3>

            {loading && (
                <div className="space-y-2 animate-pulse">
                    <div className="h-3 bg-slate-100 rounded w-full" />
                    <div className="h-3 bg-slate-100 rounded w-5/6" />
                    <div className="h-3 bg-slate-100 rounded w-3/4" />
                </div>
            )}

            {error && <p className="text-sm text-red-600">{error}</p>}

            {!loading && summary && (
                <div className="space-y-4">
                    <section>
                        <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                            Overview
                        </h4>
                        <p className="text-sm text-slate-700">{summary.overview}</p>
                    </section>

                    <section>
                        <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                            Key Points
                        </h4>
                        <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                            {summary.key_points.map((point, i) => (
                                <li key={i}>{point}</li>
                            ))}
                        </ul>
                    </section>

                    <section>
                        <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                            Main Topics
                        </h4>
                        <div className="flex flex-wrap gap-2">
                            {summary.main_topics.map((topic, i) => (
                                <span
                                    key={i}
                                    className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded-full"
                                >
                                    {topic}
                                </span>
                            ))}
                        </div>
                    </section>

                    <section>
                        <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                            Takeaways
                        </h4>
                        <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                            {summary.takeaways.map((takeaway, i) => (
                                <li key={i}>{takeaway}</li>
                            ))}
                        </ul>
                    </section>
                </div>
            )}
        </div>
    )
}