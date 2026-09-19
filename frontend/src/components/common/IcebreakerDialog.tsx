import { useEffect, useState } from 'react'
import { Check, Clipboard, LoaderCircle, MessageCircle, RefreshCw, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { icebreakerService } from '@/services/icebreakerService'
import type { Icebreaker, IcebreakerRequest, IcebreakerStyle } from '@/types'
import { demoUserId } from '@/config/runtime'
import { useLocation, useParams } from 'react-router-dom'

interface IcebreakerDialogProps {
  open: boolean
  onClose: () => void
  interests: string[]
  community: string
  event?: string
  targetType?: 'group' | 'event'
  targetId?: string
}

export function IcebreakerDialog({ open, onClose, interests, community, event, targetType, targetId }: IcebreakerDialogProps) {
  const routeParams = useParams()
  const location = useLocation()
  const resolvedTargetType = targetType ?? (location.pathname.startsWith('/events/') ? 'event' : 'group')
  const resolvedTargetId = targetId ?? routeParams.id
  const [style, setStyle] = useState<IcebreakerStyle>('friendly')
  const [icebreaker, setIcebreaker] = useState<Icebreaker | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!open) return undefined
    const handleKeyDown = (keyboardEvent: KeyboardEvent) => { if (keyboardEvent.key === 'Escape') onClose() }
    window.addEventListener('keydown', handleKeyDown)
    void generate('friendly')
    window.setTimeout(() => document.querySelector<HTMLButtonElement>('[aria-label="Close conversation starter"]')?.focus(), 0)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [open])

  async function generate(nextStyle: IcebreakerStyle = style) {
    setStyle(nextStyle)
    setIsGenerating(true)
    setError('')
    setCopied(false)
    const request: IcebreakerRequest = { interests, community, event, style: nextStyle, userId: demoUserId, targetType: resolvedTargetType, targetId: resolvedTargetId }
    try { setIcebreaker(await icebreakerService.generate(request)) } catch (generationError) { setError(generationError instanceof Error ? generationError.message : 'We could not generate a starter right now.') } finally { setIsGenerating(false) }
  }

  async function copyIcebreaker() {
    if (!icebreaker) return
    try { await navigator.clipboard.writeText(icebreaker.text); setCopied(true); window.setTimeout(() => setCopied(false), 1800) } catch { setError('Copy was blocked by your browser. You can still select the text manually.') }
  }

  if (!open) return null
  return <div className="fixed inset-0 z-50 flex items-end justify-center bg-ink/45 p-0 backdrop-blur-sm sm:items-center sm:p-5" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}><div role="dialog" aria-modal="true" aria-labelledby="icebreaker-title" aria-describedby="icebreaker-subtitle" className="max-h-[92vh] w-full overflow-y-auto rounded-t-[2rem] border border-line bg-surface p-6 shadow-float sm:max-w-lg sm:rounded-2xl sm:p-8"><div className="flex items-start justify-between gap-4"><div><span className="grid h-11 w-11 place-items-center rounded-xl bg-coral/10 text-coral"><MessageCircle size={20} /></span><h2 id="icebreaker-title" className="heading mt-5 text-3xl">Break the ice</h2><p id="icebreaker-subtitle" className="mt-2 text-sm leading-6 text-ink/55">Here's a conversation starter based on your interests.</p></div><button onClick={onClose} aria-label="Close conversation starter" className="rounded-full p-2 text-ink/45 transition hover:bg-ink/5 hover:text-ink"><X size={19} /></button></div><div className="mt-6 flex flex-wrap gap-2"><Badge className="bg-coral/10 text-coral">{community}</Badge>{event && <Badge className="bg-mint/10 text-mint">{event}</Badge>}</div><div className="mt-5 rounded-xl bg-canvas p-4"><p className="text-xs font-extrabold uppercase tracking-widest text-ink/40">Your interests</p><div className="mt-3 flex flex-wrap gap-2">{interests.map((interest) => <Badge key={interest}>{interest}</Badge>)}</div></div><div className="mt-5"><p className="mb-3 text-xs font-extrabold uppercase tracking-widest text-ink/40">Style</p><div className="grid grid-cols-3 gap-2">{(['casual', 'friendly', 'professional'] as const).map((option) => <button key={option} onClick={() => void generate(option)} className={`rounded-xl border px-2 py-3 text-xs font-extrabold capitalize transition ${style === option ? 'border-ink bg-ink text-white' : 'border-line text-ink/55 hover:border-ink/30'}`}>{option}</button>)}</div></div>{isGenerating ? <div className="my-8 flex min-h-28 flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-line text-center"><LoaderCircle size={22} className="animate-spin text-coral" /><p className="text-sm font-bold text-ink/55">Writing something that sounds like you...</p></div> : error ? <div className="my-5 rounded-xl border border-coral/30 bg-coral/10 p-4 text-sm font-semibold text-ink/70">{error}<button onClick={() => void generate()} className="mt-3 block font-extrabold text-coral">Try again</button></div> : <div className="my-5 rounded-2xl border border-sun/50 bg-sun/10 p-5"><p className="text-xs font-extrabold uppercase tracking-widest text-coral">Generated icebreaker</p><p className="mt-3 text-base font-bold leading-7 text-ink">“{icebreaker?.text}”</p><p className="mt-3 text-xs font-semibold text-ink/45">{icebreaker?.context}</p></div>}<div className="flex flex-wrap gap-2"><Button variant="outline" onClick={() => void generate()} disabled={isGenerating}><RefreshCw size={16} /> Regenerate</Button><Button variant="outline" onClick={() => void copyIcebreaker()} disabled={!icebreaker || isGenerating}>{copied ? <Check size={16} /> : <Clipboard size={16} />} {copied ? 'Copied' : 'Copy'}</Button><Button className="ml-auto" onClick={onClose} disabled={!icebreaker || isGenerating}>Use this <Check size={16} /></Button></div></div></div>
}