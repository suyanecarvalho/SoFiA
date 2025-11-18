export interface ChatMessageRequest {
  message: string
}

export interface ChatMessageResponse {
  response: string
}

export interface UIMessage {
  role: 'user' | 'assistant'
  content: string
}
