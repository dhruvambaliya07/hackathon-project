import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, CalendarDays, Check, Download, Heart, MapPin, Users } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Toast } from '@/components/ui/toast'
import { EmptyState, ErrorState, LoadingState } from '@/components/common/states'
import { EventCard } from '@/components/common/event-card'
import { IcebreakerDialog } from '@/components/common/IcebreakerDialog'
import { PageContainer } from '@/components/common/page-container'
import { eventService } from '@/services/eventService'
import { groupService } from '@/services/groupService'
import { recommendationService } from '@/services/recommendationService'
import { ApiClientError } from '@/services/apiClient'

export function EventDetailPage() {
  const { id } = useParams()
  const eventQuery = useQuery({ queryKey: ['event', id], queryFn: () => eventService.getById(id ?? '') })
  const recommendationsQuery = useQuery({ queryKey: ['recommendations-for-event', id], queryFn: recommendationService.list })
  const allEventsQuery = useQuery({ queryKey: ['events-for-related'], queryFn: eventService.list })
  const groupQueryResult = useQuery({ queryKey: ['event-group', eventQuery.data?.groupId], queryFn: () => groupService.getById(eventQuery.data?.groupId ?? ''), enabled: Boolean(eventQuery.data?.groupId) })
  const [interested, setInterested] = useState(() => id ? eventService.getInterestedIds().includes(id) : false)
  const [toastMessage, setToastMessage] = useState('')
  const [icebreakerOpen, setIcebreakerOpen] = useState(false)

  function notify(message: string) { setToastMessage(message); window.setTimeout(() => setToastMessage(''), 2400) }
  function toggleInterested() { if (!id) return; const next = eventService.toggleInterested(id); setInterested(next); notify(next ? 'You are on the attendee list.' : 'Removed from your interested events.') }
  function addToCalendar() { if (!eventQuery.data) return; eventService.downloadCalendarEvent(eventQuery.data); notify('Calendar invite downloaded.') }
  const eventNotFound = eventQuery.isError && eventQuery.error instanceof ApiClientError && eventQuery.error.status === 404

  if (eventQuery.isPending || recommendationsQuery.isPending || allEventsQuery.isPending || (Boolean(eventQuery.data) && groupQueryResult.isPending)) return <PageContainer><LoadingState label="Loading event..." /></PageContainer>
  if (eventNotFound) return <PageContainer><EmptyState title="Event not found" detail="This event may have ended or moved. Explore the other plans coming up." action={<Link to="/events"><Button variant="outline">Browse events</Button></Link>} /></PageContainer>
  if (eventQuery.isError || recommendationsQuery.isError || allEventsQuery.isError || groupQueryResult.isError) return <PageContainer><ErrorState onRetry={() => { void eventQuery.refetch(); void recommendationsQuery.refetch(); void allEventsQuery.refetch(); void groupQueryResult.refetch() }} /></PageContainer>
  if (!eventQuery.data) return <PageContainer><EmptyState title="Event not found" detail="This event may have ended or moved. Explore the other plans coming up." action={<Link to="/events"><Button variant="outline">Browse events</Button></Link>} /></PageContainer>

  const event = eventQuery.data
  const group = groupQueryResult.data
  const match = recommendationsQuery.data?.find((recommendation) => recommendation.type === 'event' && recommendation.targetId === event.id)
  const relatedEvents = allEventsQuery.data?.filter((item) => item.id !== event.id && item.groupId === event.groupId) ?? []
  const interests = match?.matchedInterests ?? event.tags

  return <PageContainer><div className="mx-auto max-w-7xl"><Link to="/events" className="mb-8 inline-flex items-center gap-2 text-sm font-bold text-ink/50 transition hover:text-ink"><ArrowLeft size={16} /> All events</Link><section className="relative overflow-hidden rounded-[2rem] bg-ink text-white shadow-float"><img src={event.imageUrl} alt={`${event.title} hero`} className="h-72 w-full object-cover opacity-65 sm:h-[28rem]" /><div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/30 to-transparent" /><div className="absolute bottom-0 left-0 right-0 p-6 sm:p-10"><p className="text-xs font-extrabold uppercase tracking-[0.18em] text-sun">{event.groupName}</p><h1 className="heading mt-3 max-w-3xl text-4xl sm:text-6xl">{event.title}</h1><div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-sm font-bold text-white/70"><span className="flex items-center gap-2"><CalendarDays size={16} /> {event.date}, {event.time}</span><span className="flex items-center gap-2"><MapPin size={16} /> {event.location}</span><span className="flex items-center gap-2"><Users size={16} /> {event.attendees} going</span></div></div></section><div className="mt-10 grid gap-10 lg:grid-cols-[1.1fr_0.9fr]"><div className="space-y-10"><section><SectionLabel>Description</SectionLabel><p className="mt-3 max-w-2xl text-base leading-8 text-ink/60">{event.description}</p></section><section><SectionLabel>Why you might enjoy this</SectionLabel><h2 className="heading mt-2 text-2xl">A good next step for your interests.</h2><div className="mt-5 grid gap-3">{match?.reasons.map((reason) => <div key={reason.label} className="rounded-xl border border-line bg-surface p-4"><p className="flex items-center gap-2 text-sm font-extrabold"><Check size={17} className="text-mint" /> {reason.label}</p><p className="mt-2 text-sm leading-6 text-ink/55">{reason.detail}</p></div>) ?? <p className="text-sm text-ink/50">Add interests to your profile to see why this event could fit.</p>}</div></section><section><SectionLabel>Matched interests</SectionLabel><div className="mt-4 flex flex-wrap gap-2">{interests.map((interest) => <Badge key={interest} className="bg-coral/10 px-3 py-2 text-coral">{interest}</Badge>)}</div></section></div><aside className="space-y-6"><Card className="p-6"><div className="flex items-center justify-between gap-4"><div><p className="eyebrow text-mint">Relevance</p><p className="heading mt-1 text-4xl text-mint">{match?.matchScore ?? '--'}<span className="text-xl">{match ? '%' : ''}</span></p></div><div className="rounded-2xl bg-mint/10 p-3 text-mint"><Heart size={22} /></div></div><Button onClick={toggleInterested} className={`mt-7 w-full ${interested ? 'bg-mint hover:bg-mint/90' : ''}`} size="lg">{interested ? <Check size={18} /> : <Heart size={18} />} {interested ? 'Interested' : "I'm Interested"}</Button><Button onClick={() => setIcebreakerOpen(true)} variant="outline" className="mt-3 w-full">Start a Conversation <Heart size={16} /></Button><Button onClick={addToCalendar} variant="outline" className="mt-3 w-full"><Download size={17} /> Add to Calendar</Button><p className="mt-3 text-center text-xs font-semibold text-ink/40">Downloads a calendar invite for this event.</p></Card>{group && <Card className="p-6"><SectionLabel>Community information</SectionLabel><div className="mt-4 flex items-center gap-3"><img src={group.imageUrl} alt="" className="h-12 w-12 rounded-xl object-cover" /><div><Link to={`/groups/${group.id}`} className="heading text-lg hover:text-coral">{group.name}</Link><p className="mt-1 text-xs font-semibold text-ink/45">{group.memberCount} members · {group.location}</p></div></div><Link to={`/groups/${group.id}`} className="mt-5 inline-flex text-sm font-extrabold text-coral">Explore community <span className="ml-2">→</span></Link></Card>}</aside></div>{relatedEvents.length > 0 && <section className="mt-12"><SectionLabel>Related events</SectionLabel><div className="mt-5 grid gap-5 md:grid-cols-2">{relatedEvents.map((relatedEvent) => <EventCard key={relatedEvent.id} event={relatedEvent} />)}</div></section>}</div><IcebreakerDialog open={icebreakerOpen} onClose={() => setIcebreakerOpen(false)} interests={interests} community={group?.name ?? event.groupName} event={event.title} /><Toast message={toastMessage} visible={Boolean(toastMessage)} /></PageContainer>
}

function SectionLabel({ children }: { children: string }) { return <p className="eyebrow text-coral">{children}</p> }
