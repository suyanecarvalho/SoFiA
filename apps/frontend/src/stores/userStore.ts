import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/features/chat/types'

interface UserState {
  user: User | null
  setUser: (user: User) => void
  clearUser: () => void
  isAuthenticated: () => boolean
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: null,
      setUser: (user) => set({ user }),
      clearUser: () => set({ user: null }),
      isAuthenticated: () => !!get().user?.id,
    }),
    {
      name: 'chat-user-storage',
    }
  )
)
