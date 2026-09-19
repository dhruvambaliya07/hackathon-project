import type { Event, Group, Recommendation, User } from '@/types'

export const currentUser: User = {
  id: 'u1', name: 'Aarav Mehta', handle: '@aaravm', avatarUrl: 'https://i.pravatar.cc/120?img=12', year: '2nd year', course: 'Computer Science',
  bio: 'Always up for a good conversation, a better playlist, and building things that matter.', interests: ['Street photography', 'Indie music', 'Design thinking', 'Football'],
}

export const groups: Group[] = [
  { id: 'g1', name: 'The Lens Club', category: 'Photography', description: 'A low-pressure space to notice more. We share photo walks, edits, and the stories behind our frames.', memberCount: 184, imageUrl: 'https://images.unsplash.com/photo-1452780212940-6f5c0d14d848?auto=format&fit=crop&w=800&q=80', accent: 'coral', tags: ['Photo walks', 'Editing', 'Storytelling'], nextEvent: 'Sunset walk this Sunday' },
  { id: 'g2', name: 'Campus Frequencies', category: 'Music', description: 'For people who believe every semester needs a soundtrack. Discover, discuss, and play together.', memberCount: 96, imageUrl: 'https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?auto=format&fit=crop&w=800&q=80', accent: 'mint', tags: ['Listening parties', 'Open mics', 'Playlists'], nextEvent: 'Open mic night on Friday' },
  { id: 'g3', name: 'Studio Common', category: 'Design', description: 'A shared table for curious makers exploring design, illustration, and the joy of making in public.', memberCount: 72, imageUrl: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?auto=format&fit=crop&w=800&q=80', accent: 'sun', tags: ['Crits', 'Workshops', 'Zines'], nextEvent: 'Zine making, 16 Nov' },
  { id: 'g4', name: 'The Long Game', category: 'Sports', description: 'Find your people on the court, track, field, or wherever you like to move.', memberCount: 211, imageUrl: 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80', accent: 'sky', tags: ['Football', 'Running', 'Badminton'], nextEvent: 'Five-a-side, tomorrow' },
]

export const events: Event[] = [
  { id: 'e1', title: 'Golden Hour Photo Walk', groupId: 'g1', groupName: 'The Lens Club', description: 'A slow wander through old campus with good light, easy conversation, and no pressure to be a pro.', date: '18 Nov', time: '4:30 PM', location: 'Meet at North Gate', imageUrl: groups[0].imageUrl, attendees: 28, tags: ['Photography', 'Beginner-friendly'] },
  { id: 'e2', title: 'Vinyl & Chai', groupId: 'g2', groupName: 'Campus Frequencies', description: 'Bring one record, one song, or just your curiosity. We are building the perfect rainy-day listening list.', date: '20 Nov', time: '6:00 PM', location: 'The Common Room', imageUrl: groups[1].imageUrl, attendees: 41, tags: ['Music', 'Social'] },
  { id: 'e3', title: 'Make a Tiny Zine', groupId: 'g3', groupName: 'Studio Common', description: 'A hands-on evening of folding, cutting, drawing, and swapping tiny publications with new friends.', date: '23 Nov', time: '3:00 PM', location: 'Design Lab 2', imageUrl: groups[2].imageUrl, attendees: 16, tags: ['Design', 'Workshop'] },
]

export const recommendations: Recommendation[] = [
  { id: 'r1', type: 'group', targetId: 'g1', title: 'The Lens Club', subtitle: 'A community for noticing the details', imageUrl: groups[0].imageUrl, matchScore: 94, reasons: [{ label: 'Shared interest', detail: 'You mentioned street photography', score: 96 }, { label: 'Good energy', detail: 'Welcomes 12 new members this month', score: 90 }], icebreakers: [{ id: 'i1', text: 'What is the last photo you took that made you stop?', context: 'A gentle opener for photo walks' }, { id: 'i2', text: 'Do you prefer finding a shot or waiting for one?', context: 'A quick way into creative process' }] },
  { id: 'r2', type: 'event', targetId: 'e2', title: 'Vinyl & Chai', subtitle: 'An evening for songs with stories', imageUrl: events[1].imageUrl, matchScore: 87, reasons: [{ label: 'Music taste', detail: 'Matches your interest in indie music', score: 88 }, { label: 'Right pace', detail: 'A small group of 41 people', score: 84 }], icebreakers: [{ id: 'i3', text: 'Which song would you play to introduce yourself?', context: 'Works beautifully over chai' }] },
]
