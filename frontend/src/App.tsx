import { useState, useEffect } from 'react'
import { checkHealth } from './api/health'
import { analyzeVideo } from './api/videos'
import { fetchTranscript } from './api/transcript'
import type { VideoMetadata } from './types/video'
import type { TranscriptResponse } from './types/transcript'

function formatDuration(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  if (hours > 0) return `${hours}h ${minutes}m`
  if (minutes > 0) return `${minutes}m ${seconds}s`
  return `${seconds}s`
}

function App() {
  const [url, setUrl] = useState('')
  const [backendStatus, setBackendStatus] = useState<'checking' | 'ok' | 'error'>('checking')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [video, setVideo] = useState<VideoMetadata | null>(null)
  const [transcript, setTranscript] = useState<TranscriptResponse | null>(null)
  const [transcriptLoading, setTranscriptLoading] = useState(false)

  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus('ok'))
      .catch(() => setBackendStatus('error'))
  }, [])

  const handleAnalyze = async () => {
    setError(null)
    setVideo(null)
    setTranscript(null)

    if (!url.trim()) {
      setError('Please paste a YouTube URL first.')
      return
    }

    setLoading(true)
    try {
      const result = await analyzeVideo(url.trim())
      setVideo(result)

      setTranscriptLoading(true)
      fetchTranscript(result.video_id)
        .then(setTranscript)
        .catch(() => setTranscript(null))
        .finally(() => setTranscriptLoading(false))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center px-4 py-16">
      <div className="w-full max-w-xl text-center">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">VideoLens</h1>
        <p className="text-slate-600 mb-8">
          Understand YouTube videos before watching.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste YouTube URL here"
            className="flex-1 px-4 py-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-400"
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="px-6 py-3 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-700 transition disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        <p className="mt-4 text-sm text-slate-400">
          Backend status:{' '}
          {backendStatus === 'checking' && 'checking...'}
          {backendStatus === 'ok' && <span className="text-green-600">connected ✓</span>}
          {backendStatus === 'error' && <span className="text-red-500">not reachable ✗</span>}
        </p>

        {error && (
          <p className="mt-6 text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm">
            {error}
          </p>
        )}

        {video && (
          <div className="mt-8 text-left bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
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
        )}

        {video && (
          <div className="mt-4 text-left bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900 mb-1">Transcript</h3>
            {transcriptLoading && (
              <p className="text-sm text-slate-400">Checking for a transcript...</p>
            )}
            {!transcriptLoading && transcript?.available && (
              <p className="text-sm text-green-700">
                Available — {transcript.snippets.length} segments
                {transcript.language ? ` (${transcript.language})` : ''}
                {transcript.is_generated ? ', auto-generated' : ''}
              </p>
            )}
            {!transcriptLoading && transcript && !transcript.available && (
              <p className="text-sm text-amber-700">
                Not available — {transcript.reason}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App