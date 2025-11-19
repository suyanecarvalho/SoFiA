import { useState, useRef, useEffect, useMemo, useEffectEvent } from 'react'
// REMOVED: import { ChatSidebar } from '@/components/chat/ChatSidebar'
import { ChatWindow } from '@/components/chat/ChatWindow'
import { MessageInput } from '@/components/chat/MessageInput'
import { ModelSelector } from '@/components/chat/ModelSelector'
import { useUIStore } from '@/stores/uiStore'
import { useUserStore } from '@/stores/userStore'
import {
  useMessages,
  useSendMessage,
} from '@/features/chat/hooks/useMessages.ts'
import { useCreateSession } from '@/features/chat/hooks/useSessions.ts'
import type { UIMessage, ModelPreference } from '@/features/chat/types'
import { toast } from 'sonner'

const Chat = () => {
  const [message, setMessage] = useState('')
  const [modelPreference, setModelPreference] =
    useState<ModelPreference>('remote')
  const [modelName, setModelName] = useState<string>('gemini-2.5-pro')
  const [optimisticFirstMessage, setOptimisticFirstMessage] =
    useState<UIMessage | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const { openModal, currentSessionId } = useUIStore()
  const isAuthenticated = useUserStore((state) => state.isAuthenticated)
  const { data: serverMessages } = useMessages(currentSessionId)
  const { mutate: sendMessage, isPending: isSending } = useSendMessage()
  const { mutateAsync: createSession, isPending: isCreating } =
    useCreateSession()

  useEffect(() => {
    if (!isAuthenticated) {
      openModal('onboarding')
    }
  }, [isAuthenticated, openModal])

  const handlePreferenceChange = (newPref: ModelPreference) => {
    setModelPreference(newPref)
    if (newPref === 'remote') {
      setModelName('gemini-2.5-pro')
    } else {
      setModelName('Mistral')
    }
  }

  const onSessionChange = useEffectEvent(() => {
    if (!currentSessionId) {
      setOptimisticFirstMessage(null)
    }
  })
  useEffect(() => {
    onSessionChange()
  }, [currentSessionId])

  const displayMessages = useMemo(() => {
    if (currentSessionId) {
      if (serverMessages && serverMessages.length > 0) {
        return serverMessages
      }
      if (optimisticFirstMessage) {
        return [optimisticFirstMessage]
      }
      return []
    }
    return optimisticFirstMessage ? [optimisticFirstMessage] : []
  }, [currentSessionId, serverMessages, optimisticFirstMessage])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [displayMessages, isSending, isCreating])

  const handleSendMessage = async (textOverride?: string) => {
    const textToSend = textOverride || message
    if (!textToSend.trim() || isSending || isCreating) return

    setMessage('')

    try {
      const sessionId = currentSessionId

      if (!sessionId) {
        setOptimisticFirstMessage({
          role: 'user',
          content: textToSend.trim(),
        })

        await createSession({
          message: textToSend.trim(),
          model_preference: modelPreference,
          model_name: modelName,
        })
      } else {
        sendMessage(
          {
            sessionId: sessionId,
            data: { message: textToSend.trim() },
          },
          {
            onError: () => {
              toast.error('Falha ao enviar mensagem. Tente novamente.')
              setMessage(textToSend)
              if (!currentSessionId) setOptimisticFirstMessage(null)
            },
          }
        )
      }
    } catch (error) {
      console.error(error)
      toast.error('Erro ao iniciar conversa')
      setOptimisticFirstMessage(null)
      setMessage(textToSend)
    }
  }

  return (
    <div className="flex h-full flex-col relative">
      {!currentSessionId && (
        <div className="absolute top-4 left-0 right-0 z-10 flex justify-center">
          <ModelSelector
            preference={modelPreference}
            model={modelName}
            onPreferenceChange={handlePreferenceChange}
            onModelChange={setModelName}
            disabled={isCreating}
          />
        </div>
      )}

      <ChatWindow
        messages={displayMessages}
        isPending={isSending || isCreating}
        handleSendMessage={handleSendMessage}
      />
      <MessageInput
        message={message}
        setMessage={setMessage}
        handleSendMessage={handleSendMessage}
        isPending={isSending || isCreating}
      />
    </div>
  )
}

export default Chat
