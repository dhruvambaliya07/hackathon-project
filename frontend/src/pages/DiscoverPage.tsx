import { Search, Sparkles } from 'lucide-react'
import { PageContainer } from '@/components/common/page-container'
import { PageHeader } from '@/components/common/page-header'
import { GroupCard } from '@/components/common/group-card'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { groups } from '@/data/mockData'

export function DiscoverPage() { return <PageContainer><PageHeader eyebrow="Explore" title="Find your thing" detail="Start with a feeling, a half-formed idea, or something you have always wanted to try." /><Card className="mb-10 border-ink bg-ink p-2 shadow-float"><div className="flex flex-col gap-2 rounded-xl bg-white/10 p-4 sm:flex-row sm:items-center"><Search className="shrink-0 text-white/60" size={22} /><input aria-label="Describe your interests" className="min-h-12 flex-1 bg-transparent px-2 text-sm text-white outline-none placeholder:text-white/45" placeholder="Try: I want to make things, meet curious people, and get better at taking photos..." /><Button variant="secondary">Find my matches <Sparkles size={16} /></Button></div></Card><div className="mb-5 flex items-center justify-between"><h2 className="heading text-2xl">Communities to explore</h2><span className="text-sm font-semibold text-ink/45">{groups.length} suggestions</span></div><div className="grid gap-5 md:grid-cols-2">{groups.map((group) => <GroupCard key={group.id} group={group} />)}</div></PageContainer> }
