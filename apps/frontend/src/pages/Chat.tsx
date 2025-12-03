import { useState, useMemo, useEffect } from 'react'
import { useParams } from 'react-router-dom'
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
import type { ModelPreference } from '@/features/chat/types'
import { toast } from 'sonner'
import { Bot, Sparkles } from 'lucide-react'

const ActiveChatHeader = ({
  modelName,
  modelPreference,
}: {
  modelName: string
  modelPreference: string
}) => (
  <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-center py-2 bg-background/80 backdrop-blur-sm border-b">
    <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted/50 px-3 py-1 rounded-full">
      {modelPreference === 'local' ? (
        <Bot className="w-4 h-4" />
      ) : (
        <Sparkles className="w-4 h-4 text-primary" />
      )}
      <span className="font-medium text-foreground">{modelName}</span>
      <span className="text-xs opacity-70">({modelPreference})</span>
    </div>
  </div>
)

const Chat = () => {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [message, setMessage] = useState('')
  const [modelPreference, setModelPreference] =
    useState<ModelPreference>('remote')
  const [modelName, setModelName] = useState<string>('gemini-2.5-pro')
  const { openModal } = useUIStore()
  const isAuthenticated = useUserStore((state) => state.isAuthenticated())
  const { data: serverMessages } = useMessages(sessionId || null)
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

  const displayMessages = useMemo(() => {
    if (!sessionId) return []
    return serverMessages || []
  }, [serverMessages, sessionId])

  const handleSendMessage = async (textOverride?: string) => {
    const textToSend = textOverride || message
    if (!textToSend.trim() || isSending || isCreating) return

    setMessage('')

    try {
      if (!sessionId) {
        await createSession({
          message: textToSend.trim(),
          model_preference: modelPreference,
          model_name: modelName,
        })
      } else {
        sendMessage(
          {
            sessionId: sessionId,
            data: {
              message: textToSend.trim(),
              model_preference: modelPreference,
              model_name: modelName,
            },
          },
          {
            onError: () => {
              toast.error('Falha ao enviar mensagem.')
              setMessage(textToSend)
            },
          }
        )
      }
    } catch (error) {
      console.error(error)
      toast.error('Erro ao iniciar conversa')
      setMessage(textToSend)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setMessage(suggestion)
  }

  return (
    <div className="flex h-full flex-col relative">
      {!sessionId ? (
        <div className="absolute top-4 left-0 right-0 z-10 flex justify-center">
          <ModelSelector
            preference={modelPreference}
            model={modelName}
            onPreferenceChange={handlePreferenceChange}
            onModelChange={setModelName}
            disabled={isCreating}
          />
        </div>
      ) : (
        <ActiveChatHeader
          modelName={modelName}
          modelPreference={modelPreference}
        />
      )}

      <div className="flex-1 overflow-hidden relative pt-10">
        <ChatWindow
          messages={displayMessages}
          isPending={isSending || isCreating}
          handleSendMessage={handleSendMessage}
        />
      </div>

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
