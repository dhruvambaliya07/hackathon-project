import type { PropsWithChildren } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DialogProps extends PropsWithChildren { open: boolean; onClose: () => void; title: string }
export function Dialog({ open, onClose, title, children }: DialogProps) { if (!open) return null; return <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-5 backdrop-blur-sm"><div className="w-full max-w-lg rounded-2xl border border-line bg-surface p-6 shadow-float"><div className="flex items-center justify-between"><h2 className="heading text-xl">{title}</h2><button onClick={onClose} aria-label="Close dialog" className={cn('rounded-full p-2 text-ink/50 hover:bg-ink/5 hover:text-ink')}><X size={18} /></button></div><div className="mt-5">{children}</div></div></div> }
