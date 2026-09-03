import type { TranscriptResponse } from '../types/transcript'
import type { TranscriptChunk } from '../types/chunk'
import type { EmbeddingStatus } from '../types/embedding'

interface TranscriptStatusProps {
    loading: boolean
    transcript: TranscriptResponse | null
    chunks: TranscriptChunk[] | null
    chunksLoading: boolean
    embeddingStatus: EmbeddingStatus | null
}

export function TranscriptStatus({
    loading,
    transcript,
    chunks,
    chunksLoading,
    embeddingStatus,
}: TranscriptStatusProps) {
    return (
        <div className="text-left bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900 mb-1">Transcript</h3>

            {loading && <p className="text-sm text-slate-400">Checking for a transcript...</p>}

            {!loading && transcript?.available && (
                <div className="text-sm text-green-700">
                    <p>
                        Available — {transcript.snippets.length} segments
                        {transcript.language ? ` (${transcript.language})` : ''}
                        {transcript.is_generated ? ', auto-generated' : ''}
                    </p>
                    {chunksLoading && <p className="text-slate-400 mt-1">Chunking transcript...</p>}
                    {!chunksLoading && chunks && (
                        <p className="text-slate-600 mt-1">
                            Grouped into {chunks.length} chunks (~
                            {Math.round(
                                chunks.reduce((sum, c) => sum + (c.end_time - c.start_time), 0) / chunks.length
                            )}
                            s avg. length)
                        </p>
                    )}
                    {embeddingStatus && (
                        <p className="text-slate-600 mt-1">
                            Embedded {embeddingStatus.embedded_chunks}/{embeddingStatus.total_chunks} chunks for search
                        </p>
                    )}
                </div>
            )}

            {!loading && transcript && !transcript.available && (
                <p className="text-sm text-amber-700">Not available — {transcript.reason}</p>
            )}
        </div>
    )
}