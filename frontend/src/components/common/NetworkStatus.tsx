import { useEffect, useState } from 'react'
import { WifiOff } from 'lucide-react'

export function NetworkStatus() {
  const [offline, setOffline] = useState(() => typeof navigator !== 'undefined' && !navigator.onLine)
  useEffect(() => { const handleOffline = () => setOffline(true); const handleOnline = () => setOffline(false); window.addEventListener('offline', handleOffline); window.addEventListener('online', handleOnline); return () => { window.removeEventListener('offline', handleOffline); window.removeEventListener('online', handleOnline) } }, [])
  if (!offline) return null
  return <div role="status" className="fixed inset-x-0 top-0 z-[60] flex items-center justify-center gap-2 bg-ink px-4 py-2 text-xs font-bold text-white"><WifiOff size={14} className="text-sun" /> You are offline. Your saved activity is available, and we will reconnect when you are back online.</div>
}
