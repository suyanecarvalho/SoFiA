import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sessionService } from '../services/sessionService'
import { useUserStore } from '@/stores/userStore'
import { useUIStore } from '@/stores/uiStore'
import type {
  ChatSession,
  UpdateSessionRequest,
  CreateSessionRequest,
} from '../types'

export function useSessions() {
  const user = useUserStore((state) => state.user)

  return useQuery({
    queryKey: ['sessions', user?.id],
    queryFn: () => {
      if (!user?.id) return []
      return sessionService.getSessions(user.id)
    },
    enabled: !!user?.id,
  })
}

export function useCreateSession() {
  const queryClient = useQueryClient()
  const user = useUserStore((state) => state.user)
  const { setCurrentSessionId } = useUIStore()

  return useMutation({
    mutationFn: (data: Omit<CreateSessionRequest, 'user_id'>) => {
      if (!user?.id) throw new Error('User not found')
      return sessionService.createSession({ ...data, user_id: user.id })
    },
    onSuccess: (newSession) => {
      queryClient.invalidateQueries({ queryKey: ['sessions', user?.id] })
      setCurrentSessionId(newSession.id)
      queryClient.invalidateQueries({ queryKey: ['messages', newSession.id] })
    },
  })
}

export function useDeleteSession() {
  const queryClient = useQueryClient()
  const user = useUserStore((state) => state.user)
  const { currentSessionId, setCurrentSessionId } = useUIStore()

  return useMutation({
    mutationFn: (sessionId: string) => sessionService.deleteSession(sessionId),
    onMutate: async (sessionId) => {
      await queryClient.cancelQueries({ queryKey: ['sessions', user?.id] })

      const previousSessions = queryClient.getQueryData<ChatSession[]>([
        'sessions',
        user?.id,
      ])

      queryClient.setQueryData<ChatSession[]>(['sessions', user?.id], (old) =>
        old ? old.filter((session) => session.id !== sessionId) : []
      )

      if (currentSessionId === sessionId) {
        setCurrentSessionId(null)
      }

      return { previousSessions }
    },
    onError: (_err, _newTodo, context) => {
      queryClient.setQueryData(
        ['sessions', user?.id],
        context?.previousSessions
      )
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions', user?.id] })
    },
  })
}

export function useUpdateSession() {
  const queryClient = useQueryClient()
  const user = useUserStore((state) => state.user)

  return useMutation({
    mutationFn: ({
      sessionId,
      data,
    }: {
      sessionId: string
      data: UpdateSessionRequest
    }) => sessionService.updateSession(sessionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions', user?.id] })
    },
  })
}
