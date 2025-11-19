import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import type { UIMessage } from '@/features/chat/types'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Bot, User } from 'lucide-react'

interface ChatWindowProps {
  messages: UIMessage[]
  isPending: boolean
  handleSendMessage: (text?: string) => void
}

export function ChatWindow({ messages, isPending }: ChatWindowProps) {
  return (
    <ScrollArea className="flex-1 p-4">
      <div className="space-y-4 max-w-3xl mx-auto">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground mt-20">
            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Comece uma conversa com o SofIA.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={cn(
              'flex w-full gap-4 p-4 rounded-lg',
              msg.role === 'assistant' ? 'bg-muted/50' : 'bg-background'
            )}
          >
            <Avatar className="w-8 h-8 border">
              {msg.role === 'assistant' ? (
                <>
                  <AvatarImage src="/bot-avatar.png" />
                  <AvatarFallback>
                    <Bot className="w-4 h-4" />
                  </AvatarFallback>
                </>
              ) : (
                <>
                  <AvatarImage src="/user-avatar.png" />
                  <AvatarFallback>
                    <User className="w-4 h-4" />
                  </AvatarFallback>
                </>
              )}
            </Avatar>
            <div className="flex-1 space-y-2">
              <p className="text-sm font-medium leading-none">
                {msg.role === 'assistant' ? 'SofIA' : 'Você'}
              </p>
              <div className="text-sm text-foreground/90 whitespace-pre-wrap">
                {msg.content}
              </div>
            </div>
          </div>
        ))}

        {isPending && (
          <div className="flex w-full gap-4 p-4 rounded-lg bg-muted/50 animate-pulse">
            <Avatar className="w-8 h-8">
              <AvatarFallback>
                <Bot className="w-4 h-4" />
              </AvatarFallback>
            </Avatar>
            <div className="space-y-2 flex-1">
              <div className="h-4 bg-foreground/10 rounded w-24"></div>
              <div className="h-4 bg-foreground/10 rounded w-full"></div>
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
  )
}
