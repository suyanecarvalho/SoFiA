import apiClient from '@/lib/api/api-client'
import type { ChatMessageRequest, ChatMessageResponse } from '../types/index'

export const chatService = {
  sendMessage: async (
    payload: ChatMessageRequest
  ): Promise<ChatMessageResponse> => {
    const { data } = await apiClient.post<ChatMessageResponse>(
      '/api/v1/chat/message',
      payload
    )
    return data
  },
}
