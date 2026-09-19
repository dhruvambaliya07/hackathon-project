import { cn } from '@/lib/utils'
import { SafeImage } from '@/components/common/SafeImage'

interface AvatarProps { src: string; alt: string; size?: 'sm' | 'md' | 'lg'; className?: string }
export function Avatar({ src, alt, size = 'md', className }: AvatarProps) { return <SafeImage src={src} alt={alt} fallbackLabel="Avatar unavailable" className={cn('rounded-full object-cover ring-4 ring-white', size === 'sm' && 'h-8 w-8', size === 'md' && 'h-10 w-10', size === 'lg' && 'h-20 w-20', className)} /> }
