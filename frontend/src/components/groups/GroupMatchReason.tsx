import { CheckCircle2 } from 'lucide-react'
import type { RecommendationReason } from '@/types'

export function GroupMatchReason({ reason }: { reason: RecommendationReason }) { return <div className="flex gap-3 rounded-xl border border-line bg-surface p-4"><CheckCircle2 className="mt-0.5 shrink-0 text-mint" size={18} /><div><p className="text-sm font-extrabold">{reason.label}</p><p className="mt-1 text-sm leading-6 text-ink/55">{reason.detail}</p></div></div> }
