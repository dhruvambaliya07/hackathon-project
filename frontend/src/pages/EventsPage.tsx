import { CalendarPlus } from 'lucide-react'
import { PageContainer } from '@/components/common/page-container'
import { PageHeader } from '@/components/common/page-header'
import { EventCard } from '@/components/common/event-card'
import { Button } from '@/components/ui/button'
import { useEvents } from '@/hooks/useApi'
import { LoadingState, ErrorState } from '@/components/common/states'

export function EventsPage() { const query = useEvents(); return <PageContainer><PageHeader eyebrow="What's happening" title="Make plans" detail="Low-stakes ways to show up, try something new, and leave with a story." action={<Button><CalendarPlus size={17} /> Add to calendar</Button>} />{query.isPending ? <LoadingState /> : query.isError ? <ErrorState onRetry={() => void query.refetch()} /> : <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{query.data?.map((event) => <EventCard key={event.id} event={event} />)}</div>}</PageContainer> }
