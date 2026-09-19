import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Bookmark, CalendarDays, Check, Edit3, Heart, MapPin, Sparkles, Users, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Avatar } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { EmptyState, ErrorState, LoadingState } from '@/components/common/states'
import { EventCard } from '@/components/common/event-card'
import { GroupCard } from '@/components/common/group-card'
import { PageContainer } from '@/components/common/page-container'
import { currentUser } from '@/data/mockData'
import { eventService } from '@/services/eventService'
import { groupService } from '@/services/groupService'
import { profileInterestOptions, profileService } from '@/services/profileService'
import { recommendationService } from '@/services/recommendationService'

type ProfileTab = 'saved' | 'events'
const CalendarIcon = CalendarDays

export function ProfilePage() {
  const queryClient = useQueryClient()
  const profileQuery = useQuery({ queryKey: ['profile'], queryFn: profileService.getProfile })
  const groupsQuery = useQuery({ queryKey: ['profile-groups'], queryFn: groupService.list })
  const eventsQuery = useQuery({ queryKey: ['profile-events'], queryFn: eventService.list })
  const recommendationsQuery = useQuery({ queryKey: ['profile-recommendations'], queryFn: recommendationService.list })
  const [editing, setEditing] = useState(false)
  const [tab, setTab] = useState<ProfileTab>('saved')
  const [selectedInterests, setSelectedInterests] = useState<string[]>([])
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => { if (profileQuery.data && !editing) setSelectedInterests(profileQuery.data.signals.map((signal) => signal.name)) }, [editing, profileQuery.data])

  async function saveInterests() {
    setIsSaving(true)
    await profileService.updateInterests(selectedInterests)
    await queryClient.invalidateQueries({ queryKey: ['profile'] })
    await queryClient.invalidateQueries({ queryKey: ['recommendation-profile'] })
    await queryClient.invalidateQueries({ queryKey: ['recommendation-feed'] })
    await queryClient.invalidateQueries({ queryKey: ['recommendations-for-groups'] })
    await queryClient.invalidateQueries({ queryKey: ['recommendations-for-events'] })
    setIsSaving(false)
    setEditing(false)
  }

  if (profileQuery.isPending || groupsQuery.isPending || eventsQuery.isPending || recommendationsQuery.isPending) return <PageContainer><LoadingState label="Loading your profile..." /></PageContainer>
  if (profileQuery.isError || groupsQuery.isError || eventsQuery.isError || recommendationsQuery.isError) return <PageContainer><ErrorState onRetry={() => { void profileQuery.refetch(); void groupsQuery.refetch(); void eventsQuery.refetch(); void recommendationsQuery.refetch() }} /></PageContainer>
  if (!profileQuery.data || !groupsQuery.data || !eventsQuery.data || !recommendationsQuery.data) return <PageContainer><EmptyState title="Your profile is still taking shape" detail="Add a few interests to start building your personal space." /></PageContainer>

  const profile = profileQuery.data
  const savedGroupIds = groupService.getSavedIds()
  const interestedEventIds = eventService.getInterestedIds()
  const interestedGroupIds = groupService.getInterestedIds()
  const savedGroups = groupsQuery.data.filter((group) => savedGroupIds.includes(group.id))
  const interestedEvents = eventsQuery.data.filter((event) => interestedEventIds.includes(event.id))
  const interestedGroups = groupsQuery.data.filter((group) => interestedGroupIds.includes(group.id))
  const recentRecommendations = recommendationsQuery.data.slice(0, 3)

  return <PageContainer><div className="mx-auto max-w-7xl"><div className="mb-9 flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><p className="eyebrow mb-3 text-coral">Your corner</p><h1 className="heading text-4xl sm:text-5xl">Your profile</h1><p className="mt-3 text-sm leading-6 text-ink/55">Keep your interests fresh and your next connection close.</p></div><Button variant={editing ? 'primary' : 'outline'} onClick={() => setEditing((current) => !current)}>{editing ? <X size={16} /> : <Edit3 size={16} />} {editing ? 'Close editor' : 'Edit profile'}</Button></div><Card className="overflow-hidden border-ink bg-ink text-white shadow-float"><div className="flex flex-col gap-6 p-6 sm:flex-row sm:items-center sm:p-8"><Avatar src={currentUser.avatarUrl} alt={currentUser.name} size="lg" className="ring-4 ring-white/15" /><div className="flex-1"><p className="text-sm font-extrabold text-sun">{currentUser.handle}</p><h2 className="heading mt-1 text-3xl">{currentUser.name}</h2><p className="mt-2 flex items-center gap-2 text-xs font-semibold text-white/50"><MapPin size={13} /> {currentUser.course} · {currentUser.year}</p><p className="mt-4 max-w-2xl text-sm leading-6 text-white/65">{currentUser.bio}</p></div><div className="rounded-2xl bg-white/10 p-5 text-center"><p className="text-3xl font-extrabold text-sun">{profile.signals.length}</p><p className="mt-1 text-xs font-bold text-white/55">active interests</p></div></div></Card>{editing && <InterestEditor selected={selectedInterests} setSelected={setSelectedInterests} onSave={() => void saveInterests()} isSaving={isSaving} />}<section className="mt-10"><div className="mb-5"><p className="eyebrow text-coral">Interest profile</p><h2 className="heading mt-1 text-3xl">What makes you, you.</h2></div><div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]"><Card className="p-6"><h3 className="heading text-xl">Interest strengths</h3><div className="mt-6 grid gap-5">{profile.signals.map((signal) => <div key={signal.id}><div className="mb-2 flex justify-between text-sm font-bold"><span>{signal.name}</span><span className="text-ink/45">{signal.score}%</span></div><div className="h-2 overflow-hidden rounded-full bg-ink/5"><div className={`h-full rounded-full ${signal.color === 'coral' ? 'bg-coral' : signal.color === 'mint' ? 'bg-mint' : signal.color === 'sun' ? 'bg-sun' : 'bg-sky'}`} style={{ width: `${signal.score}%` }} /></div></div>)}</div></Card><div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-1"><ProfileList title="Goals" items={profile.goals} icon={Sparkles} color="bg-sun/20 text-ink" /><ProfileList title="Traits" items={profile.traits} icon={Heart} color="bg-coral/10 text-coral" /></div></div></section><section className="mt-14"><div className="mb-5"><p className="eyebrow text-coral">Your library</p><h2 className="heading mt-1 text-3xl">Saved and interested</h2></div><div className="mb-6 flex gap-2 border-b border-line pb-3"><TabButton active={tab === 'saved'} onClick={() => setTab('saved')}><Bookmark size={15} /> Saved Communities</TabButton><TabButton active={tab === 'events'} onClick={() => setTab('events')}><Heart size={15} /> Interested Events</TabButton></div>{tab === 'saved' ? savedGroups.length ? <div className="grid gap-5 md:grid-cols-2">{savedGroups.map((group) => <GroupCard key={group.id} group={group} />)}</div> : <EmptyState title="No saved communities yet" detail="Save a community when it feels like a place you could belong." /> : interestedEvents.length ? <div className="grid gap-5 md:grid-cols-2">{interestedEvents.map((event) => <EventCard key={event.id} event={event} />)}</div> : <EmptyState title="No interested events yet" detail="Tap I'm Interested on an event to keep it close." />}</section><section className="mt-14"><div className="mb-5"><p className="eyebrow text-coral">Your activity</p><h2 className="heading mt-1 text-3xl">Things you've leaned toward</h2></div><div className="grid gap-6 lg:grid-cols-2"><ActivityCard title="Communities interested in" icon={Users} count={interestedGroups.length}>{interestedGroups.length ? interestedGroups.map((group) => <Link key={group.id} to={`/groups/${group.id}`} className="flex items-center gap-3 rounded-xl bg-canvas p-3"><img src={group.imageUrl} alt="" className="h-10 w-10 rounded-lg object-cover" /><span className="text-sm font-bold">{group.name}</span></Link>) : <EmptyState title="No communities yet" detail="Start a conversation from a community page." />}</ActivityCard><ActivityCard title="Events interested in" icon={CalendarIcon} count={interestedEvents.length}>{interestedEvents.length ? interestedEvents.map((event) => <Link key={event.id} to={`/events/${event.id}`} className="flex items-center gap-3 rounded-xl bg-canvas p-3"><span className="grid h-10 w-10 place-items-center rounded-lg bg-white text-center text-xs font-extrabold text-coral">{event.date.split(' ')[0]}</span><span className="text-sm font-bold">{event.title}</span></Link>) : <EmptyState title="No events yet" detail="Find a plan that sounds like you." />}</ActivityCard></div><Card className="mt-6 p-6"><div className="flex items-center justify-between"><div><p className="eyebrow">Recent recommendations</p><h3 className="heading mt-1 text-xl">A few things picked for you</h3></div><Link to="/recommendations" className="text-sm font-extrabold text-coral">See all</Link></div><div className="mt-5 grid gap-3 sm:grid-cols-3">{recentRecommendations.map((recommendation) => <div key={recommendation.id} className="rounded-xl bg-canvas p-4"><p className="text-xs font-extrabold text-coral">{recommendation.matchScore}% match</p><p className="mt-2 text-sm font-bold">{recommendation.title}</p></div>)}</div></Card></section></div></PageContainer>
}

function InterestEditor({ selected, setSelected, onSave, isSaving }: { selected: string[]; setSelected: (interests: string[]) => void; onSave: () => void; isSaving: boolean }) { return <Card className="mt-6 border-coral/30 bg-coral/5 p-6"><div className="flex items-center justify-between gap-4"><div><p className="eyebrow text-coral">Edit interests</p><h2 className="heading mt-1 text-2xl">Tune your matches</h2></div><Button onClick={onSave} disabled={isSaving || !selected.length}>{isSaving ? 'Saving...' : <><Check size={16} /> Save interests</>}</Button></div><p className="mt-2 text-sm text-ink/55">Add or remove signals to change the communities and events we recommend.</p><div className="mt-5 flex flex-wrap gap-2">{profileInterestOptions.map((interest) => { const active = selected.includes(interest); return <button key={interest} onClick={() => setSelected(active ? selected.filter((item) => item !== interest) : [...selected, interest])} className={`rounded-full border px-4 py-2 text-sm font-bold transition ${active ? 'border-ink bg-ink text-white' : 'border-line bg-surface text-ink/55 hover:border-ink/30'}`}>{active && <Check size={14} className="mr-1 inline" />}{interest}</button> })}</div></Card> }
function ProfileList({ title, items, icon: Icon, color }: { title: string; items: string[]; icon: typeof Sparkles; color: string }) { return <Card className="p-6"><div className="flex items-center gap-3"><span className={`grid h-10 w-10 place-items-center rounded-xl ${color}`}><Icon size={18} /></span><h3 className="heading text-xl">{title}</h3></div><div className="mt-5 flex flex-wrap gap-2">{items.map((item) => <Badge key={item}>{item}</Badge>)}</div></Card> }
function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) { return <button onClick={onClick} className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-extrabold transition ${active ? 'bg-ink text-white' : 'text-ink/45 hover:bg-ink/5'}`}>{children}</button> }
function ActivityCard({ title, icon: Icon, count, children }: { title: string; icon: typeof Users; count: number; children: React.ReactNode }) { return <Card className="p-6"><div className="flex items-center justify-between"><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-mint/10 text-mint"><Icon size={18} /></span><h3 className="heading text-xl">{title}</h3></div><span className="text-sm font-extrabold text-ink/40">{count}</span></div><div className="mt-5 grid gap-2">{children}</div></Card> }
