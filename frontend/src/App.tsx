import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AppLayout } from '@/layouts/AppLayout'
import { LoadingState } from '@/components/common/states'
import { NetworkStatus } from '@/components/common/NetworkStatus'
import { RouteErrorBoundary } from '@/components/common/RouteErrorBoundary'

const HomePage = lazy(() => import('@/pages/HomePage').then((module) => ({ default: module.HomePage })))
const DiscoverPage = lazy(() => import('@/pages/DiscoverPage').then((module) => ({ default: module.DiscoverPage })))
const RecommendationsPage = lazy(() => import('@/pages/RecommendationsPage').then((module) => ({ default: module.RecommendationsPage })))
const GroupsPage = lazy(() => import('@/pages/GroupsPage').then((module) => ({ default: module.GroupsPage })))
const EventsPage = lazy(() => import('@/pages/EventsPage').then((module) => ({ default: module.EventsPage })))
const ProfilePage = lazy(() => import('@/pages/ProfilePage').then((module) => ({ default: module.ProfilePage })))
const GroupDetailPage = lazy(() => import('@/pages/GroupDetailPage').then((module) => ({ default: module.GroupDetailPage })))
const EventDetailPage = lazy(() => import('@/pages/EventDetailPage').then((module) => ({ default: module.EventDetailPage })))

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 60_000, retry: 1 } } })
export function App() { return <QueryClientProvider client={queryClient}><BrowserRouter><NetworkStatus /><RouteErrorBoundary><Suspense fallback={<LoadingState label="Opening Aatmoday Connect..." />}><Routes><Route element={<AppLayout />}><Route path="/" element={<HomePage />} /><Route path="/discover" element={<DiscoverPage />} /><Route path="/recommendations" element={<RecommendationsPage />} /><Route path="/groups" element={<GroupsPage />} /><Route path="/groups/:id" element={<GroupDetailPage />} /><Route path="/events" element={<EventsPage />} /><Route path="/events/:id" element={<EventDetailPage />} /><Route path="/profile" element={<ProfilePage />} /><Route path="*" element={<Navigate to="/" replace />} /></Route></Routes></Suspense></RouteErrorBoundary></BrowserRouter></QueryClientProvider> }
