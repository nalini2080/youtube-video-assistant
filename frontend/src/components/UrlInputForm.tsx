interface UrlInputFormProps {
    url: string
    onUrlChange: (url: string) => void
    query: string
    onQueryChange: (query: string) => void
    onSubmit: () => void
    loading: boolean
}

export function UrlInputForm({
    url,
    onUrlChange,
    query,
    onQueryChange,
    onSubmit,
    loading,
}: UrlInputFormProps) {
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') onSubmit()
    }

    return (
        <div className="space-y-3">
            <input
                type="text"
                value={url}
                onChange={(e) => onUrlChange(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Paste YouTube URL here"
                className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-400"
            />
            <input
                type="text"
                value={query}
                onChange={(e) => onQueryChange(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="What are you looking for? (optional)"
                className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-400"
            />
            <button
                onClick={onSubmit}
                disabled={loading}
                className="w-full px-6 py-3 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-700 transition disabled:opacity-50"
            >
                {loading ? 'Analyzing...' : 'Analyze'}
            </button>
        </div>
    )
}