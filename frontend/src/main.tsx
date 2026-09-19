import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@/index.css'
import { App } from '@/App'

window.addEventListener('error', (event) => {
	const image = event.target
	if (!(image instanceof HTMLImageElement) || image.dataset.fallbackApplied) return
	image.dataset.fallbackApplied = 'true'
	image.alt = image.alt || 'Image unavailable'
	image.src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22600%22 height=%22360%22 viewBox=%220 0 600 360%22%3E%3Crect width=%22600%22 height=%22360%22 fill=%22%23edf1f0%22/%3E%3Ccircle cx=%22300%22 cy=%22150%22 r=%2244%22 fill=%22%23d8dfdd%22/%3E%3Cpath d=%22M278 150h44M300 128v44%22 stroke=%22%2384918d%22 stroke-width=%2212%22 stroke-linecap=%22round%22/%3E%3C/svg%3E'
}, true)

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
