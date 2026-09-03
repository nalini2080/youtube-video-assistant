import { useState, useEffect } from 'react'
import { checkHealth } from './api/health'
import { analyzeVideo } from './api/videos'
import { fetchTranscript } from './api/transcript'
import { fetchChunks } from './api/chunks'
import { fetchSummary } from './api/summary'
import { fetchRelevance } from './api/relevance'
import { fetchPersonalizedSummary } from './api/personalizedSummary'
import { fetchEmbeddingStatus } from './api/embeddings'
import { UrlInputForm } from './components/UrlInputForm'
import { EmptyState } from './components/EmptyState'
import { VideoMetadataCard } from './components/VideoMetadataCard'
import { TranscriptStatus } from './components/TranscriptStatus'
import { SummaryCard } from './components/SummaryCard'
import { RelevanceCard } from './components/RelevanceCard'
import { PersonalizedSummaryCard } from './components/PersonalizedSummaryCard'
import { ChatPanel } from './components/ChatPanel'
import type { VideoMetadata } from './types/video'
import type { TranscriptResponse } from './types/transcript'
import type { TranscriptChunk } from './types/chunk'
import type { VideoSummary } from './types/summary'
import type { RelevanceResult } from './types/relevance'
import type { PersonalizedSummaryResult } from './types/personalizedSummary'
import type { EmbeddingStatus } from './types/embedding'

function App() {
  const [url, setUrl] = useState('')
  const [query, setQuery] = useState('')
  const [backendStatus, setBackendStatus] = useState<'checking' | 'ok' | 'error'>('checking')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [video, setVideo] = useState<VideoMetadata | null>(null)
  const [transcript, setTranscript] = useState<TranscriptResponse | null>(null)
  const [transcriptLoading, setTranscriptLoading] = useState(false)
  const [chunks, setChunks] = useState<TranscriptChunk[] | null>(null)
  const [chunksLoading, setChunksLoading] = useState(false)
  const [embeddingStatus, setEmbeddingStatus] = useState<EmbeddingStatus | null>(null)
  const [summary, setSummary] = useState<VideoSummary | null>(null)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [summaryError, setSummaryError] = useState<string | null>(null)
  const [relevance, setRelevance] = useState<RelevanceResult | null>(null)
  const [relevanceLoading, setRelevanceLoading] = useState(false)
  const [relevanceError, setRelevanceError] = useState<string | null>(null)
  const [personalizedSummary, setPersonalizedSummary] = useState<PersonalizedSummaryResult | null>(null)
  const [personalizedSummaryLoading, setPersonalizedSummaryLoading] = useState(false)
  const [personalizedSummaryError, setPersonalizedSummaryError] = useState<string | null>(null)

  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus('ok'))
      .catch(() => setBackendStatus('error'))
  }, [])

  const handleAnalyze = async () => {
    setError(null)
    setVideo(null)
    setTranscript(null)
    setChunks(null)
    setEmbeddingStatus(null)
    setSummary(null)
    setSummaryError(null)
    setRelevance(null)
    setRelevanceError(null)
    setPersonalizedSummary(null)
    setPersonalizedSummaryError(null)

    if (!url.trim()) {
      setError('Please paste a YouTube URL first.')
      return
    }

    const trimmedQuery = query.trim()

    setLoading(true)
    try {
      const result = await analyzeVideo(url.trim())
      setVideo(result)

      setTranscriptLoading(true)
      fetchTranscript(result.video_id)
        .then((t) => {
          setTranscript(t)
          if (t.available) {
            setChunksLoading(true)
            fetchChunks(result.video_id)
              .then(setChunks)
              .catch(() => setChunks(null))
              .finally(() => setChunksLoading(false))

            fetchEmbeddingStatus(result.video_id)
              .then(setEmbeddingStatus)
              .catch(() => setEmbeddingStatus(null))

            setSummaryLoading(true)
            fetchSummary(result.video_id)
              .then(setSummary)
              .catch((err) =>
                setSummaryError(err instanceof Error ? err.message : 'Failed to generate summary.')
              )
              .finally(() => setSummaryLoading(false))

            if (trimmedQuery) {
              setRelevanceLoading(true)
              fetchRelevance(result.video_id, trimmedQuery)
                .then(setRelevance)
                .catch((err) =>
                  setRelevanceError(err instanceof Error ? err.message : 'Failed to analyze relevance.')
                )
                .finally(() => setRelevanceLoading(false))

              setPersonalizedSummaryLoading(true)
              fetchPersonalizedSummary(result.video_id, trimmedQuery)
                .then(setPersonalizedSummary)
                .catch((err) =>
                  setPersonalizedSummaryError(
                    err instanceof Error ? err.message : 'Failed to generate personalized summary.'
                  )
                )
                .finally(() => setPersonalizedSummaryLoading(false))
            }
          }
        })
        .catch(() => setTranscript(null))
        .finally(() => setTranscriptLoading(false))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  const hasResults = video !== null

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center px-4 py-16">
      <div className="w-full max-w-xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">VideoLens</h1>
          <p className="text-slate-600 mb-8">
            Understand YouTube videos before watching.
          </p>

          <UrlInputForm
            url={url}
            onUrlChange={setUrl}
            query={query}
            onQueryChange={setQuery}
            onSubmit={handleAnalyze}
            loading={loading}
          />

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
        </div>

        {!hasResults && !loading && !error && <EmptyState />}

        {video && (
          <div className="mt-8 space-y-4">
            {(relevance || relevanceLoading || relevanceError) && (
              <RelevanceCard
                loading={relevanceLoading}
                error={relevanceError}
                relevance={relevance}
                videoId={video.video_id}
              />
            )}

            {(personalizedSummary || personalizedSummaryLoading || personalizedSummaryError) && (
              <PersonalizedSummaryCard
                loading={personalizedSummaryLoading}
                error={personalizedSummaryError}
                personalizedSummary={personalizedSummary}
                videoId={video.video_id}
              />
            )}

            <VideoMetadataCard video={video} />

            <TranscriptStatus
              loading={transcriptLoading}
              transcript={transcript}
              chunks={chunks}
              chunksLoading={chunksLoading}
              embeddingStatus={embeddingStatus}
            />

            {transcript?.available && (
              <SummaryCard loading={summaryLoading} error={summaryError} summary={summary} />
            )}

            {transcript?.available && <ChatPanel videoId={video.video_id} />}
          </div>
        )}
      </div>
    </div>
  )
}

export default App