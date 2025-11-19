import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { messageService } from '../services/messageService'
import type { Message, SendMessageRequest } from '../types'

export function useMessages(sessionId: string | null) {
  return useQuery({
    queryKey: ['messages', sessionId],
    queryFn: () => {
      if (!sessionId) return []
      return messageService.getMessages(sessionId)
    },
    enabled: !!sessionId,
  })
}

export function useSendMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      sessionId,
      data,
    }: {
      sessionId: string
      data: SendMessageRequest
    }) => messageService.sendMessage(sessionId, data),
    onMutate: async ({ sessionId, data }) => {
      await queryClient.cancelQueries({ queryKey: ['messages', sessionId] })

      const previousMessages = queryClient.getQueryData<Message[]>([
        'messages',
        sessionId,
      ])

      // Optimistic update
      const optimisticUserMessage: Message = {
        id: `temp-${Date.now()}`,
        session_id: sessionId,
        role: 'user',
        content: data.message,
        model_name: null,
        created_at: new Date().toISOString(),
      }

      queryClient.setQueryData<Message[]>(['messages', sessionId], (old) =>
        old ? [...old, optimisticUserMessage] : [optimisticUserMessage]
      )

      return { previousMessages }
    },
    onError: (_err, variables, context) => {
      queryClient.setQueryData(
        ['messages', variables.sessionId],
        context?.previousMessages
      )
    },
    onSuccess: (data, variables) => {
      queryClient.setQueryData<Message[]>(
        ['messages', variables.sessionId],
        (old) => {
          if (!old) return [data.user_message, data.assistant_message]
          const filtered = old.filter((m) => !m.id.startsWith('temp-'))
          return [...filtered, data.user_message, data.assistant_message]
        }
      )
    },
  })
}
