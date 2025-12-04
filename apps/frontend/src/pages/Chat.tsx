import { useState, useRef, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Send } from 'lucide-react'
import { toast } from 'sonner'

import SuggestionCard from '../components/SuggestionCard'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import MessageBubble from '../components/MessageBubble'
import TypingIndicator from '../components/TypingIndicator'

import { useMessages, useSendMessage } from '@/features/chat/hooks/useMessages'
import { useCreateSession } from '@/features/chat/hooks/useSessions'
import { useChatStore } from '@/stores/chatStore'

const Chat = () => {
  const { sessionId: urlSessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const [message, setMessage] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  
  const { activeSessionId, setActiveSessionId } = useChatStore()
  
  // Use sessionId from URL or from store
  const sessionId = urlSessionId || activeSessionId
  
  // If we have a stored session but no URL, navigate to it
  useEffect(() => {
    if (!urlSessionId && activeSessionId) {
      navigate(`/chat/${activeSessionId}`, { replace: true })
    }
  }, [urlSessionId, activeSessionId, navigate])
  
  // Update store when URL changes
  useEffect(() => {
    if (urlSessionId) {
      setActiveSessionId(urlSessionId)
    }
  }, [urlSessionId, setActiveSessionId])
  
  const { data: serverMessages } = useMessages(sessionId || null)
  const { mutate: sendMessage, isPending: isSending } = useSendMessage()
  const { mutateAsync: createSession, isPending: isCreating } =
    useCreateSession()
  const isTyping = isSending || isCreating
  const displayMessages = useMemo(() => {
    return serverMessages || []
  }, [serverMessages])
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [displayMessages, isTyping])

  const handleSendMessage = async (textOverride?: string) => {
    const textToSend = textOverride || message
    if (!textToSend.trim() || isTyping) return
    setMessage('')

    try {
      if (!sessionId) {
        await createSession({
          message: textToSend.trim(),
          model_preference: 'remote',
        })
      } else {
        sendMessage(
          {
            sessionId: sessionId,
            data: {
              message: textToSend.trim(),
              model_preference: 'remote',
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
      setMessage(textToSend)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion)
  }

  const suggestions = [
    'Criar meta Viagem R$ 300/mês',
    'Quanto gastei em transporte este mês?',
    'Adicionar gasto com alimentação',
    'Como economizar 100 reais por semana?',
  ]

  return (
    <div className="flex flex-col h-full">
      <header className="px-8 py-6 border-b border-border">
        <h1 className="text-xl font-semibold text-foreground">SofIA</h1>
      </header>
      <div className="flex-1 overflow-hidden flex flex-col bg-background">
        {displayMessages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center px-8 pb-32">
            <div className="w-full max-w-3xl space-y-8">
              <h2 className="text-4xl font-bold text-center text-foreground">
                Como posso lhe ajudar?
              </h2>
              <div>
                <h3 className="text-lg font-semibold mb-4 text-foreground">
                  Sugestões rápidas
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {suggestions.map((suggestion, index) => (
                    <SuggestionCard
                      key={index}
                      text={suggestion}
                      onClick={() => handleSuggestionClick(suggestion)}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-6">
            <div className="max-w-3xl mx-auto">
              {displayMessages.map((msg) => (
                <MessageBubble
                  key={msg.id}
                  role={msg.role}
                  content={msg.content}
                />
              ))}
              {isTyping && <TypingIndicator />}
            </div>
          </div>
        )}
      </div>
      <div className="px-8 pb-8 bg-background">
        <div className="max-w-3xl mx-auto space-y-2">
          <div className="relative">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) =>
                e.key === 'Enter' && !e.shiftKey && handleSendMessage(undefined)
              }
              placeholder="Digite uma mensagem"
              className="pr-12 py-6 rounded-full border-2 focus-visible:ring-primary"
              disabled={isTyping}
            />
            <Button
              onClick={() => handleSendMessage(undefined)}
              size="icon"
              disabled={isTyping || !message.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full h-9 w-9"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Chat
