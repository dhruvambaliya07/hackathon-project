import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Bookmark, CalendarDays, Check, Heart, MapPin, Users } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Toast } from '@/components/ui/toast'
import { EmptyState, ErrorState, LoadingState } from '@/components/common/states'
import { EventCard } from '@/components/common/event-card'
import { IcebreakerDialog } from '@/components/common/IcebreakerDialog'
import { PageContainer } from '@/components/common/page-container'
import { GroupMatchReason } from '@/components/groups/GroupMatchReason'
import { groupService } from '@/services/groupService'
import { recommendationService } from '@/services/recommendationService'
import { eventService } from '@/services/eventService'

export function GroupDetailPage() {
  const { id } = useParams()
  const groupQuery = useQuery({ queryKey: ['group', id], queryFn: () => groupService.getById(id ?? '') })
  const recommendationsQuery = useQuery({ queryKey: ['recommendations-for-group', id], queryFn: recommendationService.list })
  const eventsQuery = useQuery({ queryKey: ['group-events', id], queryFn: eventService.list })
  const [interested, setInterested] = useState(() => id ? groupService.getInterestedIds().includes(id) : false)
  const [saved, setSaved] = useState(() => id ? groupService.getSavedIds().includes(id) : false)
  const [toastMessage, setToastMessage] = useState('')
  const [icebreakerOpen, setIcebreakerOpen] = useState(false)

  function notify(message: string) { setToastMessage(message); window.setTimeout(() => setToastMessage(''), 2400) }
  function toggleInterested() { if (!id) return; const next = groupService.toggleInterested(id); setInterested(next); notify(next ? 'You are on the interested list.' : 'Removed from your interested communities.') }
  function toggleSaved() { if (!id) return; const next = groupService.toggleSaved(id); setSaved(next); notify(next ? 'Community saved for later.' : 'Community removed from saved.') }

  if (groupQuery.isPending || recommendationsQuery.isPending || eventsQuery.isPending) return <PageContainer><LoadingState label="Loading community..." /></PageContainer>
  if (groupQuery.isError || recommendationsQuery.isError || eventsQuery.isError) return <PageContainer><ErrorState onRetry={() => { void groupQuery.refetch(); void recommendationsQuery.refetch(); void eventsQuery.refetch() }} /></PageContainer>
  if (!groupQuery.data) return <PageContainer><EmptyState title="Community not found" detail="This community may have moved. Head back to explore what is active now." /></PageContainer>

  const group = groupQuery.data
  const match = recommendationsQuery.data?.find((recommendation) => recommendation.type === 'group' && recommendation.targetId === group.id)
  const groupEvents = (eventsQuery.data ?? []).filter((event) => event.groupId === group.id)
  const interests = match?.matchedInterests ?? group.tags

  return <PageContainer><div className="mx-auto max-w-7xl"><Link to="/groups" className="mb-8 inline-flex items-center gap-2 text-sm font-bold text-ink/50 transition hover:text-ink"><ArrowLeft size={16} /> All communities</Link><section className="relative overflow-hidden rounded-[2rem] bg-ink text-white shadow-float"><img src={group.imageUrl} alt={`${group.name} cover`} className="h-64 w-full object-cover opacity-60 sm:h-80" /><div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/35 to-transparent" /><div className="absolute bottom-0 left-0 right-0 p-6 sm:p-10"><div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between"><div><div className="mb-4 flex items-center gap-4"><img src={group.imageUrl} alt={`${group.name} avatar`} className="h-16 w-16 rounded-2xl border-2 border-white/70 object-cover shadow sm:h-20 sm:w-20" /><div><Badge className="bg-white/90 text-ink">{group.category}</Badge><p className="mt-2 flex items-center gap-2 text-xs font-bold text-white/65"><Users size={14} /> {group.memberCount} members</p></div></div><h1 className="heading text-4xl sm:text-6xl">{group.name}</h1><p className="mt-3 flex items-center gap-2 text-sm font-semibold text-white/60"><MapPin size={15} /> {group.location ?? 'Aatmoday campus'}</p></div><div className="flex flex-wrap gap-2"><Button size="lg" variant="secondary" onClick={toggleInterested}>{interested ? <Check size={18} /> : <Heart size={18} />} {interested ? 'Interested' : "I'm Interested"}</Button><Button size="lg" className="border border-white/25 bg-white/10 text-white hover:bg-white/20" onClick={toggleSaved}>{saved ? <Check size={18} /> : <Bookmark size={18} />} {saved ? 'Saved' : 'Save'}</Button><Button size="lg" className="border border-white/25 bg-white/10 text-white hover:bg-white/20" onClick={() => setIcebreakerOpen(true)}>Start a Conversation</Button></div></div></div></section><div className="mt-10 grid gap-10 lg:grid-cols-[1.1fr_0.9fr]"><div className="space-y-10"><section><SectionLabel>About</SectionLabel><h2 className="heading mt-2 text-2xl">A place to keep showing up.</h2><p className="mt-4 max-w-2xl text-sm leading-7 text-ink/60">{group.description}</p></section><section><SectionLabel>Why you match</SectionLabel><h2 className="heading mt-2 text-2xl">A thoughtful fit, not a mystery.</h2><p className="mt-3 text-sm leading-6 text-ink/50">These signals come from your interest profile and this community's activities.</p><div className="mt-5 grid gap-3">{match?.reasons.length ? match.reasons.map((reason) => <GroupMatchReason key={reason.label} reason={reason} />) : <Card className="border-dashed p-5 text-sm text-ink/55">Add a few interests to see why this community could fit.</Card>}</div></section><section><SectionLabel>Community Activities</SectionLabel><div className="mt-4 grid gap-3 sm:grid-cols-3">{(group.activities ?? group.tags).map((activity) => <div key={activity} className="rounded-xl bg-canvas p-4 text-sm font-bold">{activity}</div>)}</div></section></div><aside className="space-y-6"><Card className="p-6"><SectionLabel>Interests</SectionLabel><div className="mt-4 flex flex-wrap gap-2">{group.tags.map((tag) => <Badge key={tag} className="bg-coral/10 px-3 py-2 text-coral">{tag}</Badge>)}</div>{match && <div className="mt-6 rounded-xl bg-mint/10 p-4"><p className="text-xs font-extrabold uppercase tracking-widest text-mint">Personal relevance</p><p className="mt-2 text-3xl font-extrabold text-mint">{match.matchScore}%</p><p className="mt-1 text-xs font-semibold text-ink/50">Based on your current interests</p></div>}</Card><Card className="p-6"><SectionLabel>Upcoming Events</SectionLabel><div className="mt-5 grid gap-4">{groupEvents.length ? groupEvents.map((event) => <Link key={event.id} to={`/events/${event.id}`} className="flex gap-3 rounded-xl bg-canvas p-3 transition hover:bg-sun/20"><span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-white text-center"><CalendarDays size={17} className="mx-auto text-coral" /><span className="block text-[9px] font-extrabold">{event.date}</span></span><span><span className="block text-sm font-extrabold">{event.title}</span><span className="mt-1 block text-xs font-semibold text-ink/45">{event.time} · {event.location}</span></span></Link>) : <p className="text-sm text-ink/50">No events announced yet.</p>}</div></Card></aside></div>{groupEvents.length > 0 && <section className="mt-12"><SectionLabel>Event previews</SectionLabel><div className="mt-5 grid gap-5 md:grid-cols-2">{groupEvents.map((event) => <EventCard key={event.id} event={event} />)}</div></section>}</div><IcebreakerDialog open={icebreakerOpen} onClose={() => setIcebreakerOpen(false)} interests={interests} community={group.name} event={groupEvents[0]?.title} /><Toast message={toastMessage} visible={Boolean(toastMessage)} /></PageContainer>
}

function SectionLabel({ children }: { children: string }) { return <p className="eyebrow text-coral">{children}</p> }
