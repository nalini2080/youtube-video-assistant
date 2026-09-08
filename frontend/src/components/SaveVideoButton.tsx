import { useState } from 'react'
import { useAuth, SignedIn } from '@clerk/clerk-react'
import { saveVideo, unsaveVideo } from '../api/history'

interface SaveVideoButtonProps {
    videoId: string
}

export function SaveVideoButton({ videoId }: SaveVideoButtonProps) {
    const { getToken } = useAuth()
    const [saved, setSaved] = useState(false)
    const [busy, setBusy] = useState(false)

    const handleToggle = async () => {
        setBusy(true)
        try {
            const token = await getToken()
            if (saved) {
                await unsaveVideo(videoId, token)
                setSaved(false)
            } else {
                await saveVideo(videoId, token)
                setSaved(true)
            }
        } catch {
            // Silently ignore — the button state just won't flip, which is a
            // clear enough signal that something went wrong for this scope.
        } finally {
            setBusy(false)
        }
    }

    return (
        <SignedIn>
            <button
                onClick={handleToggle}
                disabled={busy}
                className={`text-xs font-medium px-3 py-1.5 rounded-full border transition disabled:opacity-50 ${saved
                    ? 'bg-slate-900 text-white border-slate-900'
                    : 'bg-white text-slate-700 border-slate-300 hover:border-slate-400'
                    }`}
            >
                {saved ? '✓ Saved' : '☆ Save video'}
            </button>
        </SignedIn>
    )
}