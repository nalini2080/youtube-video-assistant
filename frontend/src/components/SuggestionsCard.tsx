import React, { useState } from 'react'
import { fetchSuggestions } from '../api/suggestions'
import type { SuggestedVideo } from '../types/suggestion'

interface SuggestionsCardProps {
    videoId: string
    missingTopics: string[]
}

export function SuggestionsCard({ videoId, missingTopics }: SuggestionsCardProps) {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [suggestions, setSuggestions] = useState<SuggestedVideo[] | null>(null)
    const [quotaExceeded, setQuotaExceeded] = useState(false)

    if (missingTopics.length === 0) return null

    const handleFind = async () => {
        setLoading(true)
        setError(null)
        try {
            const result = await fetchSuggestions(videoId, missingTopics)
            setSuggestions(result.suggestions)
            setQuotaExceeded(result.quota_exceeded)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to find suggestions.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="text-left bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900 mb-1">Fill the gaps</h3>
            <p className="text-xs text-slate-500 mb-3">
                This video doesn't cover everything — find others that do.
            </p>

            {!suggestions && !loading && (
                <button
                    onClick={handleFind}
                    className="text-sm px-4 py-2 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-700 transition"
                >
                    Find videos covering this
                </button>
            )}

            {loading && <p className="text-sm text-slate-400">Searching YouTube...</p>}

            {error && <p className="text-sm text-red-600">{error}</p>}

            {quotaExceeded && (
                <p className="text-sm text-amber-600">
                    Daily search limit reached — try again tomorrow.
                </p>
            )}

            {suggestions && suggestions.length === 0 && !quotaExceeded && (
                <p className="text-sm text-slate-400">No good matches found.</p>
            )}

            {suggestions && suggestions.length > 0 && (
                <ul className="space-y-3">
                    {suggestions.map((s) =>
                        React.createElement(
                            'a',
                            {
                                key: s.video_id,
                                href: `https://www.youtube.com/watch?v=${s.video_id}`,
                                target: '_blank',
                                rel: 'noopener noreferrer',
                                className: 'flex gap-3 group',
                            },
                            React.createElement('img', {
                                src: s.thumbnail_url,
                                alt: s.title,
                                className: 'w-24 h-auto rounded-md shrink-0',
                            }),
                            React.createElement(
                                'div',
                                { className: 'min-w-0' },
                                React.createElement(
                                    'p',
                                    { className: 'text-sm text-slate-800 group-hover:text-slate-950 leading-snug' },
                                    s.title
                                ),
                                React.createElement(
                                    'p',
                                    { className: 'text-xs text-slate-500 mt-0.5' },
                                    s.channel
                                ),
                                React.createElement(
                                    'p',
                                    { className: 'text-xs text-slate-400 mt-0.5' },
                                    `for: ${s.topic}`
                                )
                            )
                        )
                    )}
                </ul>
            )}
        </div>
    )
}