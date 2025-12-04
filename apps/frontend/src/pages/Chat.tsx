import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { ChatInputArea } from '@/features/chat/components/ChatInputArea'
import { ChatWelcomeScreen } from '@/features/chat/components/ChatWelcomeScreen'
import { ChatMessageList } from '@/features/chat/components/ChatMessageList'
import { useMessages, useSendMessage } from '@/features/chat/hooks/useMessages'
import { useCreateSession } from '@/features/chat/hooks/useSessions'
import { useChatStore } from '@/stores/chatStore'

const Chat = () => {
  const { sessionId } = useParams<{ sessionId: string }>()
  const { setActiveSessionId, clearActiveSession } = useChatStore()
  useEffect(() => {
    if (sessionId) {
      setActiveSessionId(sessionId)
    } else {
      clearActiveSession()
    }
  }, [sessionId, setActiveSessionId, clearActiveSession])
  const { data: messages = [] } = useMessages(sessionId || null)
  const { mutate: sendMessage, isPending: isSending } = useSendMessage()
  const { mutate: createSession, isPending: isCreating } = useCreateSession()
  const isTyping = isSending || isCreating
  const handleSend = (text: string) => {
    if (!text.trim()) return
    if (sessionId) {
      sendMessage(
        {
          sessionId,
          data: {
            message: text,
            model_preference: 'remote',
          },
        },
      )
    } else {
      createSession(
        {
          message: text,
          model_preference: 'remote',
        },
      )
    }
  }

  return (
    <div className="flex flex-col h-full bg-background">
      <header className="px-8 py-6 border-b border-border">
        <h1 className="text-xl font-semibold text-foreground">SofIA</h1>
      </header>
      <div className="flex-1 overflow-hidden flex flex-col relative">
        {!sessionId ? (
          <ChatWelcomeScreen onSuggestionClick={handleSend} />
        ) : (
          <ChatMessageList messages={messages} isTyping={isTyping} />
        )}
      </div>
      <ChatInputArea onSend={handleSend} isLoading={isTyping} />
    </div>
  )
}

export default Chat
