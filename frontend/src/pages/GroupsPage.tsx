import { SlidersHorizontal } from 'lucide-react'
import { PageContainer } from '@/components/common/page-container'
import { PageHeader } from '@/components/common/page-header'
import { GroupCard } from '@/components/common/group-card'
import { Button } from '@/components/ui/button'
import { useGroups } from '@/hooks/useApi'
import { LoadingState, ErrorState, EmptyState } from '@/components/common/states'

export function GroupsPage() { const query = useGroups(); return <PageContainer><PageHeader eyebrow="Communities" title="Find your people" detail="Small circles, shared rituals, and room to show up exactly as you are." action={<Button variant="outline"><SlidersHorizontal size={16} /> Filter</Button>} />{query.isPending ? <LoadingState /> : query.isError ? <ErrorState onRetry={() => void query.refetch()} /> : query.data?.length ? <div className="grid gap-5 md:grid-cols-2">{query.data.map((group) => <GroupCard key={group.id} group={group} />)}</div> : <EmptyState title="No communities yet" detail="New circles are forming all the time. Check back soon." />}</PageContainer> }
