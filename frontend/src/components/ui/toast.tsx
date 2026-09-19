import { CheckCircle2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ToastProps { message: string; visible?: boolean }
export function Toast({ message, visible = true }: ToastProps) { if (!visible) return null; return <div role="status" className={cn('fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-xl bg-ink px-4 py-3 text-sm font-bold text-white shadow-float')}><CheckCircle2 className="text-mint" size={18} />{message}</div> }
