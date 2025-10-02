import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './theme.css'      // Centralized design system - MUST load first
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
