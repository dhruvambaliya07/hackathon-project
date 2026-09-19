import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bookmark, CalendarDays, Check, ChevronDown, Heart, Lightbulb, MapPin, RefreshCw, SlidersHorizontal, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { EmptyState, ErrorState } from '@/components/common/states'
import { PageContainer } from '@/components/common/page-container'
import { MatchScore } from '@/components/recommendations/MatchScore'
import { RecommendationSkeleton } from '@/components/recommendations/RecommendationSkeleton'
import { findRecommendationContext, recommendationService } from '@/services/recommendationService'
import type { Event, Group, InterestProfile, Recommendation } from '@/types'

type FeedFilter = 'all' | 'communities' | 'events'
type FeedSort = 'recommended' | 'upcoming' | 'recent'

export function RecommendationsPage() {
  const recommendationsQuery = useQuery({ queryKey: ['recommendation-feed'], queryFn: recommendationService.list })
  const profileQuery = useQuery({ queryKey: ['recommendation-profile'], queryFn: recommendationService.getInterestProfile })
  const [filter, setFilter] = useState<FeedFilter>('all')
  const [sort, setSort] = useState<FeedSort>('recommended')
  const [category, setCategory] = useState('all')
  const [savedIds, setSavedIds] = useState(() => recommendationService.getSavedIds())
  const [interestedIds, setInterestedIds] = useState(() => recommendationService.getInterestedIds())

  const categories = useMemo(() => {
    const values = recommendationsQuery.data?.map((recommendation) => {
      const context = findRecommendationContext(recommendation)
      return context && 'category' in context ? context.category : undefined
    }).filter((value): value is string => Boolean(value)) ?? []
    return [...new Set(values)]
  }, [recommendationsQuery.data])

  const visibleRecommendations = useMemo(() => {
    const result = recommendationsQuery.data?.filter((recommendation) => {
      const typeMatch = filter === 'all' || (filter === 'communities' && recommendation.type === 'group') || (filter === 'events' && recommendation.type === 'event')
      const context = findRecommendationContext(recommendation)
      const categoryMatch = category === 'all' || (context && 'category' in context && context.category === category)
      return typeMatch && categoryMatch
    }) ?? []
    return [...result].sort((first, second) => sort === 'recommended' ? second.matchScore - first.matchScore : sort === 'recent' ? second.id.localeCompare(first.id) : first.type === 'event' ? -1 : 1)
  }, [category, filter, recommendationsQuery.data, sort])

  const communityRecommendations = visibleRecommendations.filter((recommendation) => recommendation.type === 'group')
  const eventRecommendations = visibleRecommendations.filter((recommendation) => recommendation.type === 'event')
  const featuredCommunities = communityRecommendations.slice(0, 2)
  const moreCommunities = communityRecommendations.slice(2)
  const isLoading = recommendationsQuery.isPending || profileQuery.isPending
  const isError = recommendationsQuery.isError || profileQuery.isError

  function toggleSaved(id: string) {
    const isSaved = recommendationService.toggleSaved(id)
    setSavedIds((current) => isSaved ? [...current, id] : current.filter((item) => item !== id))
  }

  function toggleInterested(id: string) {
    const isInterested = recommendationService.toggleInterested(id)
    setInterestedIds((current) => isInterested ? [...current, id] : current.filter((item) => item !== id))
  }

  return <PageContainer><div className="mx-auto max-w-7xl"><div className="mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><p className="eyebrow mb-3 text-coral">Curated for your next chapter</p><h1 className="heading text-4xl sm:text-5xl">Your Aatmoday matches</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-ink/55 sm:text-base">Based on your interests, goals, and activities you're likely to enjoy.</p></div><Link to="/discover"><Button variant="outline"><SlidersHorizontal size={16} /> Edit interests</Button></Link></div>{isLoading ? <LoadingFeed /> : isError ? <ErrorStateWithRetry onRetry={() => { void recommendationsQuery.refetch(); void profileQuery.refetch() }} /> : profileQuery.data ? <><InterestProfileCard profile={profileQuery.data} /><FeedControls filter={filter} sort={sort} category={category} categories={categories} onFilterChange={setFilter} onSortChange={setSort} onCategoryChange={setCategory} />{!visibleRecommendations.length ? <EmptyState title="Your next match is still taking shape" detail="Try adding another interest so we can find a better-fit community or event." /> : <><section className="mt-9"><SectionHeading title="Recommended Communities" detail="Groups that line up with the things you want to explore." />{featuredCommunities.length ? <div className="grid gap-6 lg:grid-cols-2">{featuredCommunities.map((recommendation) => <CommunityRecommendationCard key={recommendation.id} recommendation={recommendation} group={findRecommendationContext(recommendation) as Group} saved={savedIds.includes(recommendation.id)} interested={interestedIds.includes(recommendation.id)} onSave={() => toggleSaved(recommendation.id)} onInterested={() => toggleInterested(recommendation.id)} />)}</div> : <EmptyState title="No communities in this view" detail="Try switching the filter to All or edit your interests." />}</section><section className="mt-14"><SectionHeading title="Upcoming Events For You" detail="A few easy ways to turn a shared interest into a real plan." />{eventRecommendations.length ? <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{eventRecommendations.map((recommendation) => <EventRecommendationCard key={recommendation.id} recommendation={recommendation} event={findRecommendationContext(recommendation) as Event} saved={savedIds.includes(recommendation.id)} interested={interestedIds.includes(recommendation.id)} onSave={() => toggleSaved(recommendation.id)} onInterested={() => toggleInterested(recommendation.id)} />)}</div> : <EmptyState title="No events in this view" detail="Switch to All or check back soon for new plans." />}</section>{moreCommunities.length > 0 && <section className="mt-14"><SectionHeading title="Explore More" detail="Good matches with a little more room to surprise you." /><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{moreCommunities.map((recommendation) => <CompactCommunityCard key={recommendation.id} recommendation={recommendation} group={findRecommendationContext(recommendation) as Group} saved={savedIds.includes(recommendation.id)} onSave={() => toggleSaved(recommendation.id)} />)}</div></section>}</>}</> : null}</div></PageContainer>
}

function InterestProfileCard({ profile }: { profile: InterestProfile }) {
  return <Card className="overflow-hidden border-ink bg-ink text-white shadow-float"><div className="grid gap-7 p-6 sm:p-8 lg:grid-cols-[0.75fr_1.25fr] lg:items-center"><div><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-sun text-ink"><Lightbulb size={19} /></span><p className="eyebrow text-white/50">Your interest profile</p></div><p className="mt-4 text-sm leading-6 text-white/60">{profile.explanation}</p><Link to="/discover" className="mt-5 inline-flex items-center gap-2 text-sm font-extrabold text-sun">Refine profile <ChevronDown className="rotate-[-90deg]" size={16} /></Link></div><div className="grid gap-4 sm:grid-cols-2">{profile.signals.map((signal) => <div key={signal.id}><div className="mb-2 flex items-center justify-between gap-3"><span className="text-sm font-bold">{signal.name}</span><span className="text-xs font-extrabold text-white/55">{signal.score}%</span></div><div className="h-2 overflow-hidden rounded-full bg-white/10"><div className={`h-full rounded-full ${signal.color === 'coral' ? 'bg-coral' : signal.color === 'mint' ? 'bg-mint' : signal.color === 'sun' ? 'bg-sun' : 'bg-sky'}`} style={{ width: `${signal.score}%` }} /></div></div>)}</div></div></Card>
}

function FeedControls({ filter, sort, category, categories, onFilterChange, onSortChange, onCategoryChange }: { filter: FeedFilter; sort: FeedSort; category: string; categories: string[]; onFilterChange: (value: FeedFilter) => void; onSortChange: (value: FeedSort) => void; onCategoryChange: (value: string) => void }) {
  return <div className="mt-10 flex flex-col justify-between gap-4 border-b border-line pb-4 lg:flex-row lg:items-center"><div className="flex flex-wrap gap-2">{([['all', 'All'], ['communities', 'Communities'], ['events', 'Events']] as const).map(([value, label]) => <button key={value} onClick={() => onFilterChange(value)} className={`rounded-full px-4 py-2 text-sm font-extrabold transition ${filter === value ? 'bg-ink text-white' : 'bg-ink/5 text-ink/50 hover:bg-ink/10 hover:text-ink'}`}>{label}</button>)}</div><div className="flex flex-wrap gap-2"><label className="relative"><span className="sr-only">Category</span><select value={category} onChange={(event) => onCategoryChange(event.target.value)} className="h-10 appearance-none rounded-xl border border-line bg-surface px-3 pr-9 text-xs font-bold text-ink outline-none"><option value="all">All categories</option>{categories.map((item) => <option key={item} value={item}>{item}</option>)}</select><ChevronDown className="pointer-events-none absolute right-3 top-3 text-ink/45" size={14} /></label><label className="relative"><span className="sr-only">Sort recommendations</span><select value={sort} onChange={(event) => onSortChange(event.target.value as FeedSort)} className="h-10 appearance-none rounded-xl border border-line bg-surface px-3 pr-9 text-xs font-bold text-ink outline-none"><option value="recommended">Recommended</option><option value="upcoming">Upcoming</option><option value="recent">Recently Added</option></select><ChevronDown className="pointer-events-none absolute right-3 top-3 text-ink/45" size={14} /></label></div></div>
}

function SectionHeading({ title, detail }: { title: string; detail: string }) { return <div className="mb-6"><h2 className="heading text-2xl sm:text-3xl">{title}</h2><p className="mt-2 text-sm text-ink/50">{detail}</p></div> }

function CommunityRecommendationCard({ recommendation, group, saved, interested, onSave, onInterested }: { recommendation: Recommendation; group: Group; saved: boolean; interested: boolean; onSave: () => void; onInterested: () => void }) {
  return <Card className="group overflow-hidden transition hover:-translate-y-1 hover:shadow-float"><div className="relative h-56"><Link to={`/groups/${group.id}`}><img src={group.imageUrl} alt={`${group.name} community`} className="h-full w-full object-cover brightness-90 transition duration-500 group-hover:scale-105" /></Link><div className="absolute right-4 top-4 rounded-2xl bg-white/95 p-2 shadow"><MatchScore score={recommendation.matchScore} compact /></div><Badge className="absolute bottom-4 left-4 bg-white/95 text-ink">{group.category}</Badge></div><div className="p-6"><div className="flex items-start justify-between gap-4"><div><Link to={`/groups/${group.id}`}><h3 className="heading text-2xl transition hover:text-coral">{group.name}</h3></Link><p className="mt-2 flex items-center gap-2 text-xs font-semibold text-ink/45"><Users size={14} /> {group.memberCount} members</p></div><button onClick={onSave} aria-label={saved ? 'Remove saved community' : 'Save community'} className={`rounded-full p-2 transition ${saved ? 'bg-sun text-ink' : 'bg-ink/5 text-ink/45 hover:bg-sun'}`}><Bookmark size={17} fill={saved ? 'currentColor' : 'none'} /></button></div><p className="mt-4 text-sm leading-6 text-ink/60">{group.description}</p><div className="mt-5 flex flex-wrap gap-2">{recommendation.matchedInterests.map((interest) => <Badge key={interest} className="bg-coral/10 text-coral">{interest}</Badge>)}</div><WhyMatches reasons={recommendation.reasons} /><div className="mt-6 flex flex-wrap gap-2"><Link to={`/groups/${group.id}`} className="flex-1"><Button variant="outline" className="w-full">Explore <ChevronDown className="rotate-[-90deg]" size={15} /></Button></Link><Button onClick={onInterested} className={`flex-1 ${interested ? 'bg-mint hover:bg-mint/90' : ''}`}>{interested ? <Check size={16} /> : <Heart size={16} />} {interested ? 'Interested' : "I'm Interested"}</Button></div></div></Card>
}

function EventRecommendationCard({ recommendation, event, saved, interested, onSave, onInterested }: { recommendation: Recommendation; event: Event; saved: boolean; interested: boolean; onSave: () => void; onInterested: () => void }) {
  return <Card className="group overflow-hidden transition hover:-translate-y-1 hover:shadow-float"><div className="relative h-44"><Link to={`/events/${event.id}`}><img src={event.imageUrl} alt={`${event.title} event`} className="h-full w-full object-cover brightness-90 transition duration-500 group-hover:scale-105" /></Link><div className="absolute right-4 top-4 rounded-xl bg-white/95 p-2 shadow"><MatchScore score={recommendation.matchScore} compact /></div><div className="absolute bottom-4 left-4 rounded-xl bg-white px-3 py-2 text-center shadow"><strong className="block text-lg leading-none">{event.date.split(' ')[0]}</strong><span className="text-[10px] font-extrabold uppercase text-ink/45">Nov</span></div></div><div className="p-5"><div className="flex items-start justify-between gap-3"><div><p className="text-xs font-extrabold text-coral">{event.groupName}</p><Link to={`/events/${event.id}`}><h3 className="heading mt-1 text-xl hover:text-coral">{event.title}</h3></Link></div><button onClick={onSave} aria-label={saved ? 'Remove saved event' : 'Save event'} className={`rounded-full p-2 transition ${saved ? 'bg-sun text-ink' : 'bg-ink/5 text-ink/45 hover:bg-sun'}`}><Bookmark size={16} fill={saved ? 'currentColor' : 'none'} /></button></div><div className="mt-4 grid gap-2 text-xs font-semibold text-ink/55"><span className="flex items-center gap-2"><CalendarDays size={14} /> {event.date}, {event.time}</span><span className="flex items-center gap-2"><MapPin size={14} /> {event.location}</span></div><div className="mt-4 flex flex-wrap gap-2">{recommendation.matchedInterests.map((interest) => <Badge key={interest} className="bg-mint/10 text-mint">{interest}</Badge>)}</div><Button onClick={onInterested} variant={interested ? 'secondary' : 'outline'} className="mt-5 w-full">{interested ? <Check size={16} /> : <Heart size={16} />} {interested ? 'Interested' : "I'm Interested"}</Button></div></Card>
}

function CompactCommunityCard({ recommendation, group, saved, onSave }: { recommendation: Recommendation; group: Group; saved: boolean; onSave: () => void }) {
  return <Card className="flex gap-4 p-4 transition hover:-translate-y-1 hover:shadow-soft"><Link to={`/groups/${group.id}`} className="h-24 w-24 shrink-0 overflow-hidden rounded-xl"><img src={group.imageUrl} alt="" className="h-full w-full object-cover transition group-hover:scale-105" /></Link><div className="min-w-0 flex-1"><div className="flex items-start justify-between gap-2"><div><p className="text-[10px] font-extrabold uppercase tracking-widest text-coral">{group.category}</p><Link to={`/groups/${group.id}`}><h3 className="heading mt-1 truncate text-lg hover:text-coral">{group.name}</h3></Link></div><MatchScore score={recommendation.matchScore} compact /></div><p className="mt-2 flex items-center gap-1 text-xs font-semibold text-ink/45"><Users size={13} /> {group.memberCount} members</p><button onClick={onSave} className="mt-2 text-xs font-extrabold text-ink/45 hover:text-ink"><Bookmark size={13} className="mr-1 inline" fill={saved ? 'currentColor' : 'none'} />{saved ? 'Saved' : 'Save'}</button></div></Card>
}

function WhyMatches({ reasons }: { reasons: Recommendation['reasons'] }) { return <div className="mt-6 rounded-xl bg-canvas p-4"><div className="mb-3 flex items-center gap-2 text-xs font-extrabold uppercase tracking-widest text-ink/45"><Check size={14} className="text-mint" /> Why this matches</div><div className="grid gap-2">{reasons.map((reason) => <div key={reason.label} className="flex items-start gap-2 text-sm font-semibold text-ink/65"><span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-coral" /><span>{reason.label}: <span className="font-medium text-ink/45">{reason.detail}</span></span></div>)}</div></div> }

function LoadingFeed() { return <><div className="mt-8 h-48 animate-pulse rounded-2xl bg-ink/5" /><div className="mt-10 grid gap-6 lg:grid-cols-2"><RecommendationSkeleton /><RecommendationSkeleton /></div></> }
function ErrorStateWithRetry({ onRetry }: { onRetry: () => void }) { return <Card className="mt-8 p-8 text-center"><RefreshCw className="mx-auto text-coral" /><h2 className="heading mt-4 text-2xl">Your matches need another moment.</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-ink/55">We could not load the recommendation feed. Your interests are safe, and you can retry or edit them while we reconnect.</p><div className="mt-5 flex justify-center gap-3"><Button variant="outline" onClick={onRetry}>Try again</Button><Link to="/discover"><Button>Edit Interests</Button></Link></div></Card> }
