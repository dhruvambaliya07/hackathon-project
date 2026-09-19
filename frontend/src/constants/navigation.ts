import type { LucideIcon } from 'lucide-react'
import { Compass, CalendarDays, Users, Sparkles, UserRound } from 'lucide-react'

export interface NavigationItem {
  label: string
  href: string
  icon: LucideIcon
}

export const navigationItems: NavigationItem[] = [
  { label: 'Discover', href: '/discover', icon: Compass },
  { label: 'For you', href: '/recommendations', icon: Sparkles },
  { label: 'Communities', href: '/groups', icon: Users },
  { label: 'Events', href: '/events', icon: CalendarDays },
  { label: 'Profile', href: '/profile', icon: UserRound },
]
