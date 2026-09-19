import { useState, type FormEvent } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, ArrowUpRight, BrainCircuit, Check, Compass, MessageCircle, Search, Sparkles, Users, WandSparkles } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { EventCard } from '@/components/common/event-card'
import { GroupCard } from '@/components/common/group-card'
import { PageContainer } from '@/components/common/page-container'
import { events, groups } from '@/data/mockData'

const benefits = [
  { icon: MessageCircle, number: '01', title: 'Tell us naturally', detail: 'AI understands your interests', color: 'bg-coral text-white' },
  { icon: Compass, number: '02', title: 'Discover relevant communities', detail: 'Find groups and events that actually match', color: 'bg-mint text-white' },
  { icon: Users, number: '03', title: 'Start conversations', detail: 'Get personalized icebreakers', color: 'bg-sun text-ink' },
]

const steps = [
  { title: 'Describe', detail: 'Share the hobbies, questions, or skills you want to make more room for.', icon: WandSparkles },
  { title: 'Discover', detail: 'See communities and events chosen around your interests and your pace.', icon: Search },
  { title: 'Connect', detail: 'Show up with an easy opener and meet people who get it.', icon: Sparkles },
]

export function HomePage() {
  const navigate = useNavigate()
  const [interest, setInterest] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    navigate('/discover')
  }

  return <>
    <PageContainer>
      <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="relative overflow-hidden rounded-[2rem] bg-ink px-6 py-12 text-white shadow-float sm:px-12 sm:py-16 lg:px-16 lg:py-20">
        <div className="absolute -right-20 -top-28 h-72 w-72 rounded-full border-[52px] border-coral/60 sm:h-96 sm:w-96" />
        <div className="absolute bottom-[-100px] right-24 hidden h-56 w-56 rounded-full border-[34px] border-sun/80 lg:block" />
        <div className="relative z-[1] grid items-center gap-12 lg:grid-cols-[1fr_0.8fr]">
          <div className="max-w-2xl">
            <div className="mb-6 flex items-center gap-3 text-xs font-extrabold uppercase tracking-[0.2em] text-sun"><span className="h-px w-8 bg-sun" /> Aatmoday Connect</div>
            <h1 className="heading text-5xl leading-[1.04] sm:text-7xl">Find where you <span className="text-coral">belong.</span></h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-white/65 sm:text-lg">Discover Aatmoday communities and events that match your interests, personality, and goals.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/discover"><Button size="lg" variant="secondary">Discover My Communities <ArrowRight size={18} /></Button></Link>
              <Link to="/groups"><Button size="lg" className="border border-white/20 bg-white/10 text-white hover:bg-white/20">Explore Communities</Button></Link>
            </div>
            <div className="mt-10 flex items-center gap-3 text-sm text-white/55"><div className="flex -space-x-2"><img className="h-8 w-8 rounded-full border-2 border-ink object-cover" src="https://i.pravatar.cc/80?img=32" alt="" /><img className="h-8 w-8 rounded-full border-2 border-ink object-cover" src="https://i.pravatar.cc/80?img=47" alt="" /><img className="h-8 w-8 rounded-full border-2 border-ink object-cover" src="https://i.pravatar.cc/80?img=49" alt="" /></div><span>Join 1,800+ students finding their people</span></div>
          </div>
          <div className="relative mx-auto hidden w-full max-w-sm lg:block">
            <div className="absolute -left-7 top-12 z-[1] rounded-2xl bg-white p-3 text-ink shadow-float"><div className="flex items-center gap-2"><span className="grid h-8 w-8 place-items-center rounded-lg bg-mint/15 text-mint"><Check size={16} /></span><div><p className="text-[10px] font-extrabold uppercase tracking-wider text-ink/40">Good match</p><p className="text-xs font-extrabold">The Lens Club · 94%</p></div></div></div>
            <img src="https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=700&q=85" alt="Friends laughing together outdoors" className="h-[420px] w-full rounded-[2rem] object-cover brightness-90" />
            <div className="absolute -bottom-5 -right-5 rounded-2xl bg-sun p-4 text-ink shadow-float"><Sparkles size={20} /><p className="mt-2 text-xs font-extrabold">More you,<br />more connected.</p></div>
          </div>
        </div>
      </motion.section>

      <motion.section initial={{ opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="relative z-[2] mx-3 -mt-7 rounded-2xl border border-line bg-surface p-3 shadow-float sm:mx-10 sm:p-4">
        <form onSubmit={handleSubmit} className="rounded-xl bg-canvas p-5 sm:p-7">
          <div className="mb-4 flex items-center justify-between gap-4"><div><p className="eyebrow text-coral">Start with a thought</p><h2 className="heading mt-1 text-2xl sm:text-3xl">What are you into?</h2></div><span className="hidden rounded-full bg-sun/25 px-3 py-1 text-xs font-extrabold text-ink/60 sm:block">No right answer</span></div>
          <textarea value={interest} onChange={(event) => setInterest(event.target.value)} rows={3} className="w-full resize-none rounded-xl border border-line bg-surface p-4 text-sm leading-6 text-ink outline-none transition placeholder:text-ink/35 focus:border-coral focus:ring-4 focus:ring-coral/10" placeholder="Tell us about your hobbies, interests, skills, or what you'd like to explore..." aria-label="What are you into?" />
          <div className="mt-4 flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center"><p className="text-xs font-semibold text-ink/40">Try: “I want to make things, meet curious people, and get better at taking photos.”</p><Button type="submit" disabled={!interest.trim()}>Find My Communities <ArrowRight size={16} /></Button></div>
        </form>
      </motion.section>

      <section className="py-20 sm:py-24"><div className="mb-10 max-w-xl"><p className="eyebrow mb-3 text-coral">Less scrolling, more belonging</p><h2 className="heading text-3xl sm:text-4xl">A more human way to find your next thing.</h2></div><div className="grid gap-4 md:grid-cols-3">{benefits.map(({ icon: Icon, number, title, detail, color }) => <Card key={number} className="border-0 p-6 shadow-soft"><div className={`flex h-11 w-11 items-center justify-center rounded-xl ${color}`}><Icon size={20} /></div><p className="mt-8 text-xs font-extrabold tracking-widest text-ink/35">{number}</p><h3 className="heading mt-2 text-xl">{title}</h3><p className="mt-2 text-sm leading-6 text-ink/55">{detail}</p></Card>)}</div></section>

      <section className="border-t border-line py-20 sm:py-24"><div className="grid gap-12 lg:grid-cols-[0.7fr_1fr]"><div><p className="eyebrow mb-3 text-coral">How it works</p><h2 className="heading max-w-sm text-3xl sm:text-4xl">From “maybe someday” to “see you there.”</h2><p className="mt-5 max-w-sm text-sm leading-6 text-ink/55">The good stuff is usually one honest answer away.</p></div><div className="grid gap-8">{steps.map(({ title, detail, icon: Icon }, index) => <div key={title} className="flex gap-5"><div className="relative flex flex-col items-center"><div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-ink text-white"><Icon size={20} /></div>{index < steps.length - 1 && <div className="mt-2 h-full w-px bg-line" />}</div><div className="pb-3"><p className="text-xs font-extrabold uppercase tracking-widest text-coral">0{index + 1}</p><h3 className="heading mt-1 text-2xl">{title}</h3><p className="mt-2 max-w-lg text-sm leading-6 text-ink/55">{detail}</p></div></div>)}</div></div></section>

      <section className="pb-20 sm:pb-24"><div className="mb-7 flex items-end justify-between"><div><p className="eyebrow mb-2 text-coral">Find your people</p><h2 className="heading text-3xl sm:text-4xl">Featured communities</h2></div><Link to="/groups" className="hidden items-center gap-2 text-sm font-extrabold text-coral sm:flex">View all <ArrowRight size={16} /></Link></div><div className="grid gap-5 md:grid-cols-2">{groups.slice(0, 2).map((group) => <GroupCard key={group.id} group={group} />)}</div></section>

      <section className="pb-20 sm:pb-24"><div className="mb-7 flex items-end justify-between"><div><p className="eyebrow mb-2 text-coral">Make a plan</p><h2 className="heading text-3xl sm:text-4xl">Upcoming events</h2></div><Link to="/events" className="hidden items-center gap-2 text-sm font-extrabold text-coral sm:flex">See all events <ArrowRight size={16} /></Link></div><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{events.slice(0, 3).map((event) => <EventCard key={event.id} event={event} />)}</div></section>

      <section className="relative overflow-hidden rounded-[2rem] bg-coral px-6 py-14 text-white sm:px-12 sm:py-16"><div className="absolute right-8 top-8 opacity-20"><BrainCircuit size={120} strokeWidth={1} /></div><div className="relative max-w-xl"><p className="eyebrow text-white/65">Your next chapter starts here</p><h2 className="heading mt-3 text-4xl sm:text-5xl">Your next community is waiting.</h2><p className="mt-5 max-w-lg text-sm leading-6 text-white/75 sm:text-base">There is a room for every version of you. All you have to do is open the door.</p><Link to="/discover" className="mt-8 inline-block"><Button size="lg" variant="secondary">Start Discovering <ArrowUpRight size={18} /></Button></Link></div></section>
    </PageContainer>
  </>
}
