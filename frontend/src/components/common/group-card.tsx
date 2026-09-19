import { ArrowUpRight, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Group } from '@/types'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'

export function GroupCard({ group }: { group: Group }) { return <Card className="group overflow-hidden transition hover:-translate-y-1 hover:shadow-float"><div className="relative h-44 overflow-hidden"><img src={group.imageUrl} alt="" className="h-full w-full object-cover transition duration-500 group-hover:scale-105" /><span className="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-xs font-extrabold">{group.category}</span></div><div className="p-5"><div className="mb-3 flex items-start justify-between gap-3"><div><h3 className="heading text-xl">{group.name}</h3><p className="mt-1 flex items-center gap-1 text-xs font-semibold text-ink/45"><Users size={13} /> {group.memberCount} members</p></div><Link to={`/groups/${group.id}`} className="rounded-full bg-ink/5 p-2 transition hover:bg-sun"><ArrowUpRight size={16} /></Link></div><p className="line-clamp-2 text-sm leading-6 text-ink/60">{group.description}</p><div className="mt-4 flex flex-wrap gap-2">{group.tags.map((tag) => <Badge key={tag}>{tag}</Badge>)}</div></div></Card> }
