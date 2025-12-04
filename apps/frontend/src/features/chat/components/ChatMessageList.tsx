import { useRef, useEffect, useMemo } from 'react'
import MessageBubble from '@/components/MessageBubble'
import TypingIndicator from '@/components/TypingIndicator'
import type { Message } from '@/features/chat/types'

interface ChatMessageListProps {
  messages: Message[]
  isTyping?: boolean
}

export function ChatMessageList({ messages, isTyping }: ChatMessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const lastMessageRef = useRef<HTMLDivElement | null>(null)
  const displayMessages = useMemo(() => {
    return [...messages].sort((a, b) => {
      const dateA = new Date(a.created_at).getTime() || a.id
      const dateB = new Date(b.created_at).getTime() || b.id
      return dateA - dateB
    })
  }, [messages])
  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'end',
      })
    } else if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [displayMessages.length, isTyping])
  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-6">
      <div className="max-w-3xl mx-auto space-y-4">
        {displayMessages.map((msg, index) => {
          const isLast = index === displayMessages.length - 1
          return (
            <div
              key={msg.id ?? `msg-${index}`}
              ref={isLast ? lastMessageRef : undefined}
            >
              <MessageBubble role={msg.role} content={msg.content} />
            </div>
          )
        })}
        {isTyping && <TypingIndicator />}
      </div>
    </div>
  )
}
