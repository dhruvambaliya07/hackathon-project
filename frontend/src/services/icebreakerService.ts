import type { Icebreaker, IcebreakerRequest, IcebreakerStyle } from '@/types'
import type { ApiEnvelope, ApiIcebreaker } from '@/api/types'
import { apiClient, unwrapApiResponse } from '@/services/apiClient'
import { apiMode, demoUserId } from '@/config/runtime'

export interface IcebreakerService {
  generate(request: IcebreakerRequest): Promise<Icebreaker>
}

let generationCount = 0

const mockIcebreakerService: IcebreakerService = {
  async generate(request) {
    if (!request.interests.length || !request.community) {
      throw new Error('Add an interest and community before generating a conversation starter.')
    }

    await new Promise<void>((resolve) => window.setTimeout(resolve, 420))
    const interest = request.interests[0]
    const secondInterest = request.interests[1] ?? 'new things'
    const eventContext = request.event ? ` Are you joining ${request.event.toLowerCase()}?` : ' What have you been enjoying lately?'
    const variants = {
      casual: [`Hey! I noticed you're into ${interest} too. I'm getting into ${secondInterest}.${eventContext}`, `Hi! I saw ${interest} in your profile and had to say hello. What are you working on lately?`],
      friendly: [`Hey! I noticed we both enjoy ${interest}. I'm exploring ${secondInterest} too, and would love to hear what got you into it.${eventContext}`, `Hi there! Your interest in ${interest} caught my eye. What is your favorite part of being part of ${request.community}?`],
      professional: [`Hello! I noticed your interest in ${interest}. I'm exploring ${secondInterest} as well. Would you be open to sharing what you are learning?`, `Hello! I am interested in ${interest} and noticed you are part of ${request.community}. What would you recommend for someone getting started?`],
    }
    const text = variants[request.style][generationCount++ % variants[request.style].length]
    return { id: `icebreaker-${Date.now()}`, text, context: `Generated from ${request.interests.join(' and ')}${request.event ? ` and ${request.event}` : ''}.` }
  },
}

export const icebreakerService = mockIcebreakerService

if (apiMode === 'api') {
  icebreakerService.generate = async (request) => {
    if (!request.targetType || !request.targetId) throw new Error('A target is required to generate an icebreaker.')
    const response = await apiClient.post<{ user_id: string; target_type: 'group' | 'event'; target_id: string; style: IcebreakerStyle }, ApiEnvelope<ApiIcebreaker>>('/icebreakers', { user_id: request.userId ?? demoUserId, target_type: request.targetType, target_id: request.targetId, style: request.style })
    const result = unwrapApiResponse(response)
    return { id: `icebreaker-${Date.now()}`, text: result.icebreaker, context: `${result.style} icebreaker` }
  }
}