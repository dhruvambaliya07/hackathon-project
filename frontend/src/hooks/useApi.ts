import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'

export function useGroups() {
  return useQuery({ queryKey: ['groups'], queryFn: api.listGroups })
}

export function useEvents() {
  return useQuery({ queryKey: ['events'], queryFn: api.listEvents })
}

export function useRecommendations() {
  return useQuery({ queryKey: ['recommendations'], queryFn: api.listRecommendations })
}
