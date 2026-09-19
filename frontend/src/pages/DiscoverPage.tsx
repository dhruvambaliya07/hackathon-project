import { useEffect, useState, type FormEvent } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { AlertCircle, ArrowLeft, ArrowRight, Check, ChevronRight, CircleHelp, LoaderCircle, RefreshCw, Sparkles, Target, Users, WandSparkles } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { PageContainer } from '@/components/common/page-container'
import { interestService } from '@/services/interestService'
import type { InterestProfile } from '@/types'

const suggestions = [
  'I love photography and filmmaking...',
  'I enjoy coding and building things...',
  'I like music, dance and meeting new people...',
  "I'm interested in entrepreneurship and finance...",
]

const analysisSteps = ['Understanding your interests...', 'Finding communities...', 'Building your recommendations...']
const manualOptions = ['Photography', 'Technology', 'Music', 'Design', 'Entrepreneurship', 'Sports']
type DiscoverStage = 'form' | 'analyzing' | 'profile' | 'error'

export function DiscoverPage() {
  const navigate = useNavigate()
  const [description, setDescription] = useState('')
  const [stage, setStage] = useState<DiscoverStage>('form')
  const [analysisStep, setAnalysisStep] = useState(0)
  const [profile, setProfile] = useState<InterestProfile | null>(null)
  const [error, setError] = useState('')
  const [manualInterests, setManualInterests] = useState<string[]>([])
  const analyzeMutation = useMutation({ mutationFn: (text: string) => interestService.analyze(text) })

  useEffect(() => {
    if (stage !== 'analyzing') return undefined
    const interval = window.setInterval(() => setAnalysisStep((current) => Math.min(current + 1, analysisSteps.length - 1)), 260)
    return () => window.clearInterval(interval)
  }, [stage])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!description.trim()) return
    setStage('analyzing')
    setAnalysisStep(0)
    setError('')
    try {
      const result = await analyzeMutation.mutateAsync(description)
      setProfile(result)
      setStage('profile')
    } catch (analysisError) {
      setError(analysisError instanceof Error ? analysisError.message : 'We could not analyze that just yet.')
      setStage('error')
    }
  }

  function retry() {
    setStage('form')
    setError('')
  }

  function toggleManualInterest(interest: string) {
    setManualInterests((current) => current.includes(interest) ? current.filter((item) => item !== interest) : [...current, interest])
  }

  function continueWithManualInterests() {
    setProfile(interestService.createManualProfile(manualInterests))
    setStage('profile')
  }

  if (stage === 'analyzing') return <AnalysisState currentStep={analysisStep} />
  if (stage === 'profile' && profile) return <ProfileResult profile={profile} onBack={() => setStage('form')} onContinue={() => navigate('/recommendations')} />

  return <PageContainer><div className="mx-auto max-w-4xl"><button onClick={() => navigate('/')} className="mb-8 inline-flex items-center gap-2 text-sm font-bold text-ink/50 transition hover:text-ink"><ArrowLeft size={16} /> Back home</button><div className="mb-10 max-w-2xl"><p className="eyebrow mb-3 text-coral">Step 1 of 2 · Your starting point</p><h1 className="heading text-4xl sm:text-6xl">What are you into?</h1><p className="mt-4 text-base leading-7 text-ink/55 sm:text-lg">Tell us about your hobbies, interests, skills, or the kind of people and activities you'd like to explore.</p></div>{stage === 'error' ? <ErrorPanel message={error} selected={manualInterests} onRetry={retry} onToggle={toggleManualInterest} onContinue={continueWithManualInterests} /> : <Card className="overflow-hidden border-ink shadow-float"><form onSubmit={handleSubmit} className="p-5 sm:p-8"><div className="mb-4 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-coral/10 text-coral"><WandSparkles size={19} /></span><div><p className="text-sm font-extrabold">Your interests, in your words</p><p className="text-xs font-semibold text-ink/40">There is no perfect way to phrase it.</p></div></div><textarea autoFocus value={description} onChange={(event) => setDescription(event.target.value)} rows={8} className="w-full resize-none rounded-2xl border border-line bg-canvas p-5 text-base leading-7 text-ink outline-none transition placeholder:text-ink/35 focus:border-coral focus:ring-4 focus:ring-coral/10" placeholder="Tell us about your hobbies, interests, skills, or what you'd like to explore..." aria-label="Describe your interests" /><div className="mt-5 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center"><span className="text-xs font-semibold text-ink/40">{description.length}/500 characters</span><Button type="submit" size="lg" disabled={!description.trim()}>Analyze my interests <ArrowRight size={18} /></Button></div></form><div className="border-t border-line bg-canvas/70 p-5 sm:px-8"><div className="mb-3 flex items-center gap-2 text-xs font-extrabold uppercase tracking-widest text-ink/45"><CircleHelp size={14} /> Try a starting point</div><div className="grid gap-2 sm:grid-cols-2">{suggestions.map((suggestion) => <button type="button" key={suggestion} onClick={() => setDescription(suggestion.replace('...', ''))} className="rounded-xl border border-line bg-surface px-4 py-3 text-left text-sm font-semibold text-ink/60 transition hover:-translate-y-0.5 hover:border-coral/50 hover:text-ink">{suggestion}</button>)}</div></div></Card>}<p className="mt-5 flex items-center justify-center gap-2 text-center text-xs font-semibold text-ink/40"><Sparkles size={14} className="text-coral" /> Your answer helps us explain why each match fits.</p></div></PageContainer>
}

function AnalysisState({ currentStep }: { currentStep: number }) {
  return <PageContainer><div className="flex min-h-[65vh] items-center justify-center"><motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-lg text-center"><div className="mx-auto grid h-20 w-20 place-items-center rounded-3xl bg-ink text-sun shadow-float"><LoaderCircle size={34} className="animate-spin" /></div><p className="eyebrow mt-8 text-coral">Aatmoday intelligence</p><h1 className="heading mt-3 text-3xl sm:text-4xl">{analysisSteps[currentStep]}</h1><p className="mx-auto mt-4 max-w-sm text-sm leading-6 text-ink/55">We are looking for the interests, goals, and energy behind your words.</p><div className="mt-10 grid gap-3 text-left">{analysisSteps.map((step, index) => <div key={step} className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-sm font-bold transition ${index <= currentStep ? 'border-mint/30 bg-mint/10 text-ink' : 'border-line text-ink/35'}`}>{index < currentStep ? <Check size={17} className="text-mint" /> : index === currentStep ? <LoaderCircle size={17} className="animate-spin text-coral" /> : <span className="h-[17px] w-[17px] rounded-full border border-line" />}{step}</div>)}</div></motion.div></div></PageContainer>
}

function ProfileResult({ profile, onBack, onContinue }: { profile: InterestProfile; onBack: () => void; onContinue: () => void }) {
  return <PageContainer><div className="mx-auto max-w-5xl"><div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="eyebrow mb-3 text-coral">Step 2 of 2 · Your interest profile</p><h1 className="heading text-4xl sm:text-5xl">Here is what we heard.</h1></div><Button variant="ghost" onClick={onBack}><RefreshCw size={16} /> Refine my answer</Button></div><div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]"><Card className="p-6 sm:p-8"><div className="flex items-start gap-4"><span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-mint text-white"><Sparkles size={22} /></span><div><p className="eyebrow text-mint">Our read on your interests</p><p className="mt-2 text-sm leading-6 text-ink/60">{profile.explanation}</p></div></div><div className="mt-8 grid gap-5">{profile.signals.map((signal) => <div key={signal.id}><div className="mb-2 flex items-center justify-between"><div className="flex items-center gap-2"><span className={`h-2.5 w-2.5 rounded-full ${signal.color === 'coral' ? 'bg-coral' : signal.color === 'mint' ? 'bg-mint' : signal.color === 'sun' ? 'bg-sun' : 'bg-sky'}`} /><span className="text-sm font-extrabold">{signal.name}</span><Badge>{signal.category}</Badge></div><span className="text-sm font-extrabold text-ink/55">{signal.score}%</span></div><div className="h-2 overflow-hidden rounded-full bg-ink/5"><motion.div initial={{ width: 0 }} animate={{ width: `${signal.score}%` }} transition={{ duration: 0.7, delay: 0.1 }} className={`h-full rounded-full ${signal.color === 'coral' ? 'bg-coral' : signal.color === 'mint' ? 'bg-mint' : signal.color === 'sun' ? 'bg-sun' : 'bg-sky'}`} /></div></div>)}</div></Card><div className="grid gap-6"><SignalList title="Goals" items={profile.goals} icon={Target} color="bg-coral/10 text-coral" /><SignalList title="Traits" items={profile.traits} icon={Users} color="bg-sun/20 text-ink" /></div></div><div className="mt-8 flex flex-col items-center justify-between gap-4 rounded-2xl bg-ink p-6 text-white sm:flex-row sm:px-8"><div><p className="heading text-xl">Ready to see what fits?</p><p className="mt-1 text-sm text-white/55">We'll use this profile to explain your community matches.</p></div><Button size="lg" variant="secondary" onClick={onContinue}>Show My Matches <ChevronRight size={18} /></Button></div></div></PageContainer>
}

function SignalList({ title, items, icon: Icon, color }: { title: string; items: string[]; icon: typeof Target; color: string }) {
  return <Card className="p-6"><div className="flex items-center gap-3"><span className={`grid h-10 w-10 place-items-center rounded-xl ${color}`}><Icon size={18} /></span><h2 className="heading text-xl">{title}</h2></div><div className="mt-5 grid gap-3">{items.map((item) => <div key={item} className="flex items-center gap-3 rounded-xl bg-canvas px-4 py-3 text-sm font-bold"><Check size={16} className="text-mint" /> {item}</div>)}</div></Card>
}

function ErrorPanel({ message, selected, onRetry, onToggle, onContinue }: { message: string; selected: string[]; onRetry: () => void; onToggle: (interest: string) => void; onContinue: () => void }) {
  return <Card className="border-coral/30 p-6 shadow-soft sm:p-8"><div className="flex items-start gap-4"><span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-coral/10 text-coral"><AlertCircle size={20} /></span><div><h2 className="heading text-2xl">We could not finish that.</h2><p className="mt-2 text-sm leading-6 text-ink/55">{message} You can try again, or start with a few interests below while we get things back on track.</p></div></div><div className="mt-7 flex flex-wrap gap-2">{manualOptions.map((interest) => <button type="button" key={interest} onClick={() => onToggle(interest)} className={`rounded-full border px-4 py-2 text-sm font-bold transition ${selected.includes(interest) ? 'border-ink bg-ink text-white' : 'border-line bg-surface text-ink/60 hover:border-ink/30'}`}>{selected.includes(interest) && <Check size={14} className="mr-1 inline" />}{interest}</button>)}</div><div className="mt-7 flex flex-wrap gap-3"><Button variant="outline" onClick={onRetry}><RefreshCw size={16} /> Try again</Button><Button onClick={onContinue} disabled={!selected.length}>Continue with selected interests <ArrowRight size={16} /></Button></div></Card>
}
