import { AlertCircle, Inbox, LoaderCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function LoadingState({ label = 'Finding your people...' }: { label?: string }) { return <div className="flex min-h-48 flex-col items-center justify-center gap-3 text-ink/50"><LoaderCircle className="animate-spin" size={24} /><p className="text-sm font-semibold">{label}</p></div> }
export function ErrorState({ onRetry }: { onRetry?: () => void }) { return <div className="flex min-h-48 flex-col items-center justify-center gap-3 text-center"><AlertCircle className="text-coral" /><p className="font-bold">Something went a little sideways.</p>{onRetry && <Button onClick={onRetry} variant="outline" size="sm">Try again</Button>}</div> }
export function EmptyState({ title, detail }: { title: string; detail: string }) { return <div className="flex min-h-48 flex-col items-center justify-center gap-3 text-center"><Inbox className="text-ink/30" /><p className="font-bold">{title}</p><p className="max-w-sm text-sm text-ink/50">{detail}</p></div> }
