import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../api/chat'
import { TimestampChip } from './TimestampChip'
import type { ChatSource } from '../types/chat'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  sources?: ChatSource[]
  isError?: boolean
}

interface ChatPanelProps {
  videoId: string
}

let messageIdCounter = 0
function nextMessageId(): string {
  messageIdCounter += 1
  return `msg-${messageIdCounter}`
}

export function ChatPanel({ videoId }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const trimmed = input.trim()
    if (!trimmed || sending) return

    const userMessage: ChatMessage = { id: nextMessageId(), role: 'user', text: trimmed }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setSending(true)

    try {
      const response = await sendChatMessage(videoId, trimmed)
      setMessages((prev) => [
        ...prev,
        {
          id: nextMessageId(),
          role: 'assistant',
          text: response.answer,
          sources: response.sources,
        },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: nextMessageId(),
          role: 'assistant',
          text: err instanceof Error ? err.message : 'Something went wrong answering that.',
          isError: true,
        },
      ])
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSend()
  }

  return (
    <div className="text-left bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-900 mb-3">Chat with this video</h3>

      <div className="max-h-96 overflow-y-auto space-y-3 mb-3 pr-1">
        {messages.length === 0 && (
          <p className="text-sm text-slate-400">Ask something about this video to get started.</p>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${msg.role === 'user'
                  ? 'bg-slate-900 text-white'
                  : msg.isError
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-slate-100 text-slate-800'
                }`}
            >
              <p>{msg.text}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {msg.sources.map((source, i) => (
                    <TimestampChip key={i} videoId={videoId} seconds={source.start_time} />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {sending && (
          <div className="flex justify-start">
            <div className="bg-slate-100 text-slate-500 rounded-lg px-3 py-2 text-sm">
              Thinking...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask something about this video"
          disabled={sending}
          className="flex-1 px-3 py-2 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-400 disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={sending || !input.trim()}
          className="px-4 py-2 text-sm rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-700 transition disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  )
}