import type { ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'outline'
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> { variant?: ButtonVariant; size?: 'sm' | 'md' | 'lg' }

export function Button({ className, variant = 'primary', size = 'md', ...props }: ButtonProps) {
  return <button className={cn('inline-flex items-center justify-center gap-2 rounded-xl font-bold transition hover:-translate-y-0.5 disabled:pointer-events-none disabled:opacity-50', variant === 'primary' && 'bg-ink text-white shadow-soft hover:bg-ink/90', variant === 'secondary' && 'bg-sun text-ink hover:bg-sun/80', variant === 'ghost' && 'text-ink/60 hover:bg-ink/5 hover:text-ink', variant === 'outline' && 'border border-line bg-surface text-ink hover:border-ink/30', size === 'sm' && 'min-h-9 px-3 text-xs', size === 'md' && 'min-h-11 px-4 text-sm', size === 'lg' && 'min-h-14 px-6 text-base', className)} {...props} />
}
