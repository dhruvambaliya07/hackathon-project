import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CalendarDays, ChevronDown, Search } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { EmptyState, ErrorState, LoadingState } from '@/components/common/states'
import { EventCard } from '@/components/common/event-card'
import { PageContainer } from '@/components/common/page-container'
import { eventService } from '@/services/eventService'
import { recommendationService } from '@/services/recommendationService'
import { groupService } from '@/services/groupService'

export function EventsPage() {
  const eventsQuery = useQuery({ queryKey: ['events'], queryFn: eventService.list })
  const recommendationsQuery = useQuery({ queryKey: ['recommendations-for-events'], queryFn: recommendationService.list })
  const groupsQuery = useQuery({ queryKey: ['groups-for-events'], queryFn: groupService.list })
  const [search, setSearch] = useState('')
  const [date, setDate] = useState('all')
  const [category, setCategory] = useState('all')
  const [community, setCommunity] = useState('all')
  const [location, setLocation] = useState('all')
  const matchByEvent = useMemo(() => new Map((recommendationsQuery.data ?? []).filter((recommendation) => recommendation.type === 'event').map((recommendation) => [recommendation.targetId, recommendation])), [recommendationsQuery.data])
  const groups = groupsQuery.data ?? []
  const filterOptions = useMemo(() => ({
    dates: [...new Set(eventsQuery.data?.map((event) => event.date) ?? [])],
    categories: [...new Set(eventsQuery.data?.map((event) => groups.find((group) => group.id === event.groupId)?.category).filter((value): value is string => Boolean(value)) ?? [])],
    communities: [...new Set(eventsQuery.data?.map((event) => event.groupName) ?? [])],
    locations: [...new Set(eventsQuery.data?.map((event) => event.location) ?? [])],
  }), [eventsQuery.data])
  const filteredEvents = useMemo(() => eventsQuery.data?.filter((event) => {
    const query = search.trim().toLowerCase()
    const group = groups.find((item) => item.id === event.groupId)
    const matchesSearch = !query || [event.title, event.groupName, event.location, event.description, ...event.tags].some((value) => value.toLowerCase().includes(query))
    return matchesSearch && (date === 'all' || event.date === date) && (category === 'all' || group?.category === category) && (community === 'all' || event.groupName === community) && (location === 'all' || event.location === location)
  }) ?? [], [category, community, date, eventsQuery.data, location, search])
  const isLoading = eventsQuery.isPending || recommendationsQuery.isPending || groupsQuery.isPending
  const isError = eventsQuery.isError || recommendationsQuery.isError || groupsQuery.isError

  return <PageContainer><div className="mx-auto max-w-7xl"><div className="mb-9 flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><p className="eyebrow mb-3 text-coral">Make a plan</p><h1 className="heading text-4xl sm:text-5xl">Upcoming Events</h1><p className="mt-3 max-w-xl text-sm leading-6 text-ink/55 sm:text-base">Low-pressure ways to show up, try something new, and leave with a story.</p></div><Badge className="w-fit bg-sun/25 py-2 text-ink"><CalendarDays size={14} className="mr-2" /> {eventsQuery.data?.length ?? 0} events coming up</Badge></div><Card className="border-ink bg-ink p-2 shadow-float"><div className="flex items-center gap-3 rounded-xl bg-white/10 px-4"><Search className="shrink-0 text-white/60" size={20} /><input value={search} onChange={(event) => setSearch(event.target.value)} aria-label="Search events" className="min-h-14 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-white/45" placeholder="Search events..." /></div></Card><div className="mt-5 flex flex-wrap gap-2"><FilterSelect label="Date" value={date} options={filterOptions.dates} onChange={setDate} /><FilterSelect label="Category" value={category} options={filterOptions.categories} onChange={setCategory} /><FilterSelect label="Community" value={community} options={filterOptions.communities} onChange={setCommunity} /><FilterSelect label="Location" value={location} options={filterOptions.locations} onChange={setLocation} /><button onClick={() => { setSearch(''); setDate('all'); setCategory('all'); setCommunity('all'); setLocation('all') }} className="px-3 text-xs font-extrabold text-ink/40 hover:text-ink">Clear filters</button></div>{isLoading ? <div className="mt-10"><LoadingState label="Finding upcoming events..." /></div> : isError ? <div className="mt-10"><ErrorState onRetry={() => { void eventsQuery.refetch(); void recommendationsQuery.refetch() }} /></div> : filteredEvents.length ? <><div className="mb-5 mt-10"><h2 className="heading text-2xl">Events to explore</h2><p className="mt-1 text-sm text-ink/45">{filteredEvents.length} {filteredEvents.length === 1 ? 'event' : 'events'} matching your filters</p></div><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{filteredEvents.map((event) => { const match = matchByEvent.get(event.id); return <EventCard key={event.id} event={event} matchScore={match?.matchScore} matchedInterests={match?.matchedInterests} /> })}</div></> : <Card className="mt-10 border-dashed"><EmptyState title="No events match that search" detail="Try clearing a filter or searching for a community, activity, or location." /></Card>}</div></PageContainer>
}

function FilterSelect({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) { return <label className="relative"><span className="sr-only">{label}</span><select value={value} onChange={(event) => onChange(event.target.value)} className="h-10 max-w-[180px] appearance-none rounded-xl border border-line bg-surface px-3 pr-9 text-xs font-bold text-ink outline-none transition hover:border-ink/30 focus:border-coral"><option value="all">{label}: All</option>{options.map((option) => <option key={option} value={option}>{option}</option>)}</select><ChevronDown className="pointer-events-none absolute right-3 top-3 text-ink/45" size={14} /></label> }
