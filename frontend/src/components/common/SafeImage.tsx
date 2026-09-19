import { useState } from 'react'
import { ImageOff } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SafeImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  fallbackLabel?: string
}

export function SafeImage({ src, alt, className, fallbackLabel = 'Image unavailable', ...props }: SafeImageProps) {
  const [failed, setFailed] = useState(false)
  if (failed || !src) return <div role="img" aria-label={alt || fallbackLabel} className={cn('flex items-center justify-center bg-ink/5 text-ink/35', className)}><span className="flex flex-col items-center gap-2 text-center text-xs font-bold"><ImageOff size={20} />{fallbackLabel}</span></div>
  return <img {...props} src={src} alt={alt} className={className} onError={() => setFailed(true)} />
}
