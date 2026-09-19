import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AppLayout } from '@/layouts/AppLayout'
import { HomePage } from '@/pages/HomePage'
import { DiscoverPage } from '@/pages/DiscoverPage'
import { RecommendationsPage } from '@/pages/RecommendationsPage'
import { GroupsPage } from '@/pages/GroupsPage'
import { EventsPage } from '@/pages/EventsPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { GroupDetailPage, EventDetailPage } from '@/pages/DetailPages'

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 60_000, retry: 1 } } })
export function App() { return <QueryClientProvider client={queryClient}><BrowserRouter><Routes><Route element={<AppLayout />}><Route path="/" element={<HomePage />} /><Route path="/discover" element={<DiscoverPage />} /><Route path="/recommendations" element={<RecommendationsPage />} /><Route path="/groups" element={<GroupsPage />} /><Route path="/groups/:id" element={<GroupDetailPage />} /><Route path="/events" element={<EventsPage />} /><Route path="/events/:id" element={<EventDetailPage />} /><Route path="/profile" element={<ProfilePage />} /><Route path="*" element={<Navigate to="/" replace />} /></Route></Routes></BrowserRouter></QueryClientProvider> }
