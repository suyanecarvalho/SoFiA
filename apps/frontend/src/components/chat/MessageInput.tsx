import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { SendHorizontal } from 'lucide-react'
import type { KeyboardEvent } from 'react'

interface MessageInputProps {
  message: string
  setMessage: (value: string) => void
  handleSendMessage: (textOverride?: string) => void
  isPending: boolean
}

export function MessageInput({
  message,
  setMessage,
  handleSendMessage,
  isPending,
}: MessageInputProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="p-4 border-t bg-background">
      <div className="max-w-3xl mx-auto flex gap-2">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Digite sua mensagem..."
          className="min-h-[60px] resize-none"
          disabled={isPending}
        />
        <Button
          size="icon"
          className="h-[60px] w-[60px]"
          onClick={() => handleSendMessage()}
          disabled={!message.trim() || isPending}
        >
          <SendHorizontal className="w-6 h-6" />
        </Button>
      </div>
    </div>
  )
}
