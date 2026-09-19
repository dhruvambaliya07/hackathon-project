import type { PropsWithChildren } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DialogProps extends PropsWithChildren { open: boolean; onClose: () => void; title: string }
export function Dialog({ open, onClose, title, children }: DialogProps) { if (!open) return null; return <div role="dialog" aria-modal="true" aria-labelledby="dialog-title" className="fixed inset-0 z-50 grid place-items-end bg-ink/40 p-0 backdrop-blur-sm sm:place-items-center sm:p-5"><div className="max-h-[92vh] w-full overflow-y-auto rounded-t-2xl border border-line bg-surface p-6 shadow-float sm:max-w-lg sm:rounded-2xl"><div className="flex items-center justify-between"><h2 id="dialog-title" className="heading text-xl">{title}</h2><button autoFocus onClick={onClose} aria-label="Close dialog" className={cn('rounded-full p-2 text-ink/50 hover:bg-ink/5 hover:text-ink')}><X size={18} /></button></div><div className="mt-5">{children}</div></div></div> }
