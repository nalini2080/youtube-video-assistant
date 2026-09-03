import React from 'react'
import { formatTimestamp, youtubeTimestampUrl } from '../utils/timestamps'

interface TimestampChipProps {
    videoId: string
    seconds: number
    label?: string
}

export function TimestampChip({ videoId, seconds, label }: TimestampChipProps) {
    const url = youtubeTimestampUrl(videoId, seconds)
    const text = label ?? formatTimestamp(seconds)

    return React.createElement(
        'a',
        {
            href: url,
            target: '_blank',
            rel: 'noopener noreferrer',
            className:
                'text-xs font-mono bg-slate-900 text-white px-2 py-1 rounded hover:bg-slate-700 transition inline-block',
        },
        `📍 ${text}`
    )
}