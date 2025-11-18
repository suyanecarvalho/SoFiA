import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'
import SuggestionCard from '@/components/SuggestionCard'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import MessageBubble from '@/components/MessageBubble'
import TypingIndicator from '@/components/TypingIndicator'
import type { UIMessage } from '@/features/chat/types'
import { useSendMessage } from '@/features/chat/hooks/useSendMessage.ts'

const Chat = () => {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<UIMessage[]>([])
  const scrollRef = useRef<HTMLDivElement>(null)

  // Hook integration
  const { mutate: sendMessage, isPending } = useSendMessage()

  const suggestions = [
    'Criar meta Viagem R$ 300/mês',
    'Quanto gastei em transporte este mês?',
    'Adicionar gasto com alimentação',
    'Como economizar 100 reais por semana?',
  ]

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isPending])

  const handleSendMessage = (textOverride?: string) => {
    const textToSend = textOverride || message

    if (textToSend.trim() && !isPending) {
      const userMessage: UIMessage = {
        role: 'user',
        content: textToSend.trim(),
      }
      setMessages((prev) => [...prev, userMessage])
      setMessage('')
      sendMessage(
        { message: textToSend.trim() },
        {
          onSuccess: (data) => {
            const botMessage: UIMessage = {
              role: 'assistant',
              content: data.response,
            }
            setMessages((prev) => [...prev, botMessage])
          },
        }
      )
    }
  }

  return (
    <div className="flex flex-col h-full">
      <header className="px-8 py-6 border-b">
        <h1 className="text-xl font-semibold">SofIA</h1>
      </header>

      <div className="flex-1 overflow-hidden flex flex-col">
        {messages.length === 0 ? (
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
                      onClick={() => handleSendMessage(suggestion)}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-6">
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.map((msg, index) => (
                <MessageBubble
                  key={index}
                  role={msg.role}
                  content={msg.content}
                />
              ))}
              {isPending && <TypingIndicator />}
            </div>
          </div>
        )}
      </div>

      <div className="px-8 pb-8">
        <div className="max-w-3xl mx-auto space-y-2">
          <div className="relative">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={isPending}
              placeholder={
                isPending ? 'SofIA está pensando...' : 'Digite uma mensagem'
              }
              className="pr-12 py-6 rounded-full border-2 focus-visible:ring-primary disabled:opacity-50"
            />
            <Button
              onClick={() => handleSendMessage()}
              disabled={!message.trim() || isPending}
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full h-9 w-9"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <p className="text-xs text-center text-muted-foreground">
            Utilizando modelo Finance-v1
          </p>
        </div>
      </div>
    </div>
  )
}

export default Chat
