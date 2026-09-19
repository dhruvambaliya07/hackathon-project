import type { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn('rounded-2xl border border-line bg-surface shadow-soft', className)} {...props} /> }
export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn('p-5 pb-3', className)} {...props} /> }
export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={cn('p-5 pt-2', className)} {...props} /> }
