import { useMutation } from '@tanstack/react-query'
import { chatService } from '../services/chatService'
import type { ChatMessageRequest, ChatMessageResponse } from '../types/index'
import { AxiosError } from 'axios'

export const useSendMessage = () => {
  return useMutation<ChatMessageResponse, AxiosError, ChatMessageRequest>({
    mutationFn: (payload) => chatService.sendMessage(payload),
  })
}
