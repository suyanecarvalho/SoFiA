import { Toaster } from '@/components/ui/toaster.tsx'
import { Toaster as Sonner } from '../src/components/ui/sonner'
import { TooltipProvider } from '@/components/ui/tooltip.tsx'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from '../src/components/Layout'
import Home from '../src/pages/Home'
import Chat from '../src/pages/Chat'
import Dashboard from '../src/pages/Dashboard'
import Settings from '../src/pages/Settings'
import Profile from '../src/pages/Profile'
import NotFound from '../src/pages/NotFound'
import { ModalLayer } from '@/components/ModalLayer'
import { useAuthCheck } from '@/features/auth/hooks/useAuthCheck'

const queryClient = new QueryClient()

const AppContent = () => {
  useAuthCheck()
  return (
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <ModalLayer />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </TooltipProvider>
  )
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AppContent />
  </QueryClientProvider>
)

export default App
