import { useQuery } from '@tanstack/react-query'
import { eventService } from '@/services/eventService'
import { groupService } from '@/services/groupService'
import { recommendationService } from '@/services/recommendationService'

export function useGroups() {
  return useQuery({ queryKey: ['groups'], queryFn: groupService.list })
}

export function useEvents() {
  return useQuery({ queryKey: ['events'], queryFn: eventService.list })
}

export function useRecommendations() {
  return useQuery({ queryKey: ['recommendations'], queryFn: recommendationService.list })
}
