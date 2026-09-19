import { Component, type ErrorInfo, type ReactNode } from 'react'
import { RefreshCw, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface RouteErrorBoundaryProps { children: ReactNode }
interface RouteErrorBoundaryState { hasError: boolean }

export class RouteErrorBoundary extends Component<RouteErrorBoundaryProps, RouteErrorBoundaryState> {
  state: RouteErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): RouteErrorBoundaryState { return { hasError: true } }
  componentDidCatch(_error: Error, _info: ErrorInfo) { /* Keep the user-facing fallback free of technical details. */ }
  reset = () => { this.setState({ hasError: false }); window.location.reload() }

  render() {
    if (this.state.hasError) return <div className="grid min-h-screen place-items-center bg-canvas px-5"><div className="max-w-md text-center"><span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-coral/10 text-coral"><Sparkles size={24} /></span><h1 className="heading mt-5 text-3xl">This page needs a refresh.</h1><p className="mt-3 text-sm leading-6 text-ink/55">Something interrupted this view. Your saved interests and activity are safe.</p><Button onClick={this.reset} className="mt-6"><RefreshCw size={16} /> Reload page</Button></div></div>
    return this.props.children
  }
}
