import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) { return <span className={cn('inline-flex items-center rounded-full bg-ink/5 px-3 py-1 text-xs font-bold text-ink/65', className)} {...props} /> }
