import { create } from 'zustand'

type ModalType = 'onboarding' | 'settings' | null

interface UIState {
  isSidebarOpen: boolean
  activeModal: ModalType
  currentSessionId: string | null

  toggleSidebar: () => void
  setSidebarOpen: (isOpen: boolean) => void
  openModal: (modal: ModalType) => void
  closeModal: () => void
  setCurrentSessionId: (sessionId: string | null) => void
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  activeModal: null,
  currentSessionId: null,

  toggleSidebar: () =>
    set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (isOpen) => set({ isSidebarOpen: isOpen }),
  openModal: (modal) => set({ activeModal: modal }),
  closeModal: () => set({ activeModal: null }),
  setCurrentSessionId: (sessionId) => set({ currentSessionId: sessionId }),
}))
