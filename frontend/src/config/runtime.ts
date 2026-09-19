export type ApiMode = 'api' | 'mock'

export const apiMode: ApiMode = import.meta.env.VITE_API_MODE === 'api' ? 'api' : 'mock'
export const demoUserId = import.meta.env.VITE_DEMO_USER_ID?.trim() || '89d4a21e-b315-515f-8ff3-80b56e85ed6c'