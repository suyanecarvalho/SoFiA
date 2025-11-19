import { useEffect } from 'react'
import { useUserStore } from '@/stores/userStore'
import { useUIStore } from '@/stores/uiStore'

export function useAuthCheck() {
  const isAuthenticated = useUserStore((state) => state.isAuthenticated())
  const openModal = useUIStore((state) => state.openModal)
  const activeModal = useUIStore((state) => state.activeModal)
  useEffect(() => {
    if (!isAuthenticated && !activeModal) {
      openModal('onboarding')
    }
  }, [isAuthenticated, activeModal, openModal])
}
