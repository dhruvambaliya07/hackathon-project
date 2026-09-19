import { cn } from '@/lib/utils'

interface MatchScoreProps {
  score: number
  compact?: boolean
}

export function MatchScore({ score, compact = false }: MatchScoreProps) {
  return <div className={cn('flex items-center gap-2', compact && 'gap-1.5')}><div className={cn('relative grid place-items-center rounded-full bg-mint/15 text-mint', compact ? 'h-9 w-9' : 'h-14 w-14')}><span className={cn('heading', compact ? 'text-xs' : 'text-base')}>{score}%</span></div><div className={cn('font-extrabold text-mint', compact ? 'text-[10px]' : 'text-xs')}><span className="block uppercase tracking-widest">Match</span><span className="block font-semibold text-ink/40">relevance</span></div></div>
}
