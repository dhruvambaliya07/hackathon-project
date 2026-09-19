import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CalendarDays, Check, Heart, MapPin, MessageCircle, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { EmptyState, ErrorState, LoadingState } from '@/components/common/states'
import { IcebreakerDialog } from '@/components/common/IcebreakerDialog'
import { PageContainer } from '@/components/common/page-container'
import { MatchScore } from '@/components/recommendations/MatchScore'
import { demoUserId } from '@/config/runtime'
import { eventService } from '@/services/eventService'
import { feedbackService } from '@/services/feedbackService'
import { groupService } from '@/services/groupService'
import { recommendationService } from '@/services/recommendationService'
import type { Event, Group, Recommendation } from '@/types'

type FeedFilter = 'all' | 'communities' | 'events'

export function RecommendationsPage() {
  const recommendationsQuery = useQuery({ queryKey: ['recommendation-feed', demoUserId], queryFn: recommendationService.list })
  const profileQuery = useQuery({ queryKey: ['recommendation-profile', demoUserId], queryFn: recommendationService.getInterestProfile })
  const groupsQuery = useQuery({ queryKey: ['recommendation-groups'], queryFn: groupService.list })
  const eventsQuery = useQuery({ queryKey: ['recommendation-events'], queryFn: eventService.list })
  const [filter, setFilter] = useState<FeedFilter>('all')
  const [interestedIds, setInterestedIds] = useState<string[]>([])
  const recommendations = recommendationsQuery.data ?? []
  const visible = useMemo(() => recommendations.filter((item) => filter === 'all' || (filter === 'communities' && item.type === 'group') || (filter === 'events' && item.type === 'event')), [filter, recommendations])
  const loading = recommendationsQuery.isPending || profileQuery.isPending || groupsQuery.isPending || eventsQuery.isPending
  const failed = recommendationsQuery.isError || profileQuery.isError || groupsQuery.isError || eventsQuery.isError

  async function submitInterest(recommendation: Recommendation) {
    await feedbackService.submit({ recommendationId: recommendation.id, value: 'up', feedbackType: 'interested' })
    setInterestedIds((current) => current.includes(recommendation.id) ? current : [...current, recommendation.id])
  }

  if (loading) return <PageContainer><LoadingState label="Finding your matches..." /></PageContainer>
  if (failed) return <PageContainer><ErrorState onRetry={() => { void recommendationsQuery.refetch(); void profileQuery.refetch(); void groupsQuery.refetch(); void eventsQuery.refetch() }} /></PageContainer>
  if (!profileQuery.data) return <PageContainer><EmptyState title="Your profile is still taking shape" detail="Add a few interests to start building recommendations." /></PageContainer>

  const groupById = new Map((groupsQuery.data ?? []).map((group) => [group.id, group]))
  const eventById = new Map((eventsQuery.data ?? []).map((event) => [event.id, event]))
  const communities = visible.filter((item) => item.type === 'group')
  const eventRecommendations = visible.filter((item) => item.type === 'event')

  return <PageContainer><div className="mx-auto max-w-7xl"><div className="mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><p className="eyebrow mb-3 text-coral">Curated for your next chapter</p><h1 className="heading text-4xl sm:text-5xl">Your Aatmoday matches</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-ink/55 sm:text-base">Based on your interests, goals, and activities you are likely to enjoy.</p></div><Link to="/discover"><Button variant="outline">Edit interests</Button></Link></div><div className="mb-8 grid gap-4 sm:grid-cols-3">{profileQuery.data.signals.slice(0, 3).map((signal) => <Card key={signal.id} className="p-4"><p className="text-sm font-extrabold">{signal.name}</p><p className="mt-1 text-xs font-semibold text-ink/45">{signal.score}% profile strength</p></Card>)}</div><div className="flex gap-2 border-b border-line pb-4">{([['all', 'All'], ['communities', 'Communities'], ['events', 'Events']] as const).map(([value, label]) => <button key={value} onClick={() => setFilter(value)} className={`rounded-full px-4 py-2 text-sm font-extrabold ${filter === value ? 'bg-ink text-white' : 'bg-ink/5 text-ink/50'}`}>{label}</button>)}</div>{!visible.length ? <EmptyState title="No recommendations yet" detail="Try adding another interest or describing what you want to explore." /> : <><section className="mt-9"><h2 className="heading mb-6 text-2xl sm:text-3xl">Recommended Communities</h2><div className="grid gap-6 lg:grid-cols-2">{communities.map((recommendation) => { const group = groupById.get(recommendation.targetId); return group ? <CommunityCard key={recommendation.id} recommendation={recommendation} group={group} interested={interestedIds.includes(recommendation.id)} onInterested={() => void submitInterest(recommendation)} /> : null })}</div></section><section className="mt-14"><h2 className="heading mb-6 text-2xl sm:text-3xl">Upcoming Events For You</h2><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{eventRecommendations.map((recommendation) => { const event = eventById.get(recommendation.targetId); return event ? <EventRecommendationCard key={recommendation.id} recommendation={recommendation} event={event} interested={interestedIds.includes(recommendation.id)} onInterested={() => void submitInterest(recommendation)} /> : null })}</div></section></>}</div></PageContainer>
}

function CommunityCard({ recommendation, group, interested, onInterested }: { recommendation: Recommendation; group: Group; interested: boolean; onInterested: () => void }) { const [open, setOpen] = useState(false); return <Card className="overflow-hidden"><div className="relative h-52"><Link to={`/groups/${group.id}`}><img src={group.imageUrl} alt={`${group.name} community`} className="h-full w-full object-cover" /></Link><div className="absolute right-4 top-4 rounded-2xl bg-white/95 p-2 shadow"><MatchScore score={recommendation.matchScore} compact /></div></div><div className="p-5"><p className="text-xs font-extrabold uppercase tracking-widest text-coral">{group.category}</p><Link to={`/groups/${group.id}`}><h3 className="heading mt-1 text-2xl hover:text-coral">{group.name}</h3></Link><p className="mt-1 flex items-center gap-1 text-xs font-semibold text-ink/45"><Users size={13} /> {group.memberCount} members</p><p className="mt-4 text-sm leading-6 text-ink/60">{group.description}</p><div className="mt-4 flex flex-wrap gap-2">{recommendation.matchedInterests.map((item) => <Badge key={item} className="bg-coral/10 text-coral">{item}</Badge>)}</div><p className="mt-4 text-sm font-semibold text-ink/55">{recommendation.backendExplanation}</p><div className="mt-5 flex gap-2"><Link to={`/groups/${group.id}`} className="flex-1"><Button variant="outline" className="w-full">Explore</Button></Link><Button onClick={onInterested} className={`flex-1 ${interested ? 'bg-mint' : ''}`}>{interested ? <Check size={15} /> : <Heart size={15} />} {interested ? 'Interested' : "I'm Interested"}</Button></div><Button onClick={() => setOpen(true)} variant="ghost" className="mt-2 w-full"><MessageCircle size={16} /> Start a Conversation</Button></div><IcebreakerDialog open={open} onClose={() => setOpen(false)} interests={recommendation.matchedInterests} community={group.name} targetType="group" targetId={recommendation.targetId} /></Card> }

function EventRecommendationCard({ recommendation, event, interested, onInterested }: { recommendation: Recommendation; event: Event; interested: boolean; onInterested: () => void }) { const [open, setOpen] = useState(false); return <Card className="overflow-hidden"><div className="relative h-44"><Link to={`/events/${event.id}`}><img src={event.imageUrl} alt={`${event.title} event`} className="h-full w-full object-cover" /></Link><div className="absolute right-3 top-3 rounded-2xl bg-white/95 p-2 shadow"><MatchScore score={recommendation.matchScore} compact /></div></div><div className="p-5"><p className="text-xs font-bold text-coral">{event.groupName}</p><Link to={`/events/${event.id}`}><h3 className="heading mt-1 text-xl hover:text-coral">{event.title}</h3></Link><div className="mt-4 grid gap-2 text-xs font-semibold text-ink/55"><span className="flex items-center gap-2"><CalendarDays size={14} /> {event.date}, {event.time}</span><span className="flex items-center gap-2"><MapPin size={14} /> {event.location}</span></div><div className="mt-4 flex flex-wrap gap-2">{recommendation.matchedInterests.map((item) => <Badge key={item} className="bg-mint/10 text-mint">{item}</Badge>)}</div><Button onClick={onInterested} variant={interested ? 'secondary' : 'outline'} className="mt-5 w-full">{interested ? <Check size={15} /> : <Heart size={15} />} {interested ? 'Interested' : "I'm Interested"}</Button><Button onClick={() => setOpen(true)} variant="ghost" className="mt-2 w-full"><MessageCircle size={16} /> Start a Conversation</Button></div><IcebreakerDialog open={open} onClose={() => setOpen(false)} interests={recommendation.matchedInterests} community={event.groupName} event={event.title} targetType="event" targetId={recommendation.targetId} /></Card> }
