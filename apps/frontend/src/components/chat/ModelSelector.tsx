import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Cpu, Cloud } from 'lucide-react'
import type { ModelPreference } from '@/features/chat/types'

interface ModelSelectorProps {
  preference: ModelPreference
  model: string
  onPreferenceChange: (val: ModelPreference) => void
  onModelChange: (val: string) => void
  disabled?: boolean
}

const MODEL_OPTIONS = {
  remote: [
    { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro' },
    { value: 'gemini-2.0-flash-lite', label: 'Gemini 2.0 Flash Lite' },
  ],
  local: [
    { value: 'Mistral', label: 'Mistral' },
    { value: 'llama', label: 'Llama' },
  ],
}

export function ModelSelector({
  preference,
  model,
  onPreferenceChange,
  onModelChange,
  disabled,
}: ModelSelectorProps) {
  return (
    <div className="flex items-center gap-2 p-2 bg-muted/30 rounded-lg border mb-4 w-fit">
      <Tabs
        value={preference}
        onValueChange={(v) => onPreferenceChange(v as ModelPreference)}
        className="w-fit"
      >
        <TabsList className="h-8">
          <TabsTrigger
            value="remote"
            disabled={disabled}
            className="px-3 text-xs"
          >
            <Cloud className="w-3 h-3 mr-2" />
            Remote
          </TabsTrigger>
          <TabsTrigger
            value="local"
            disabled={disabled}
            className="px-3 text-xs"
          >
            <Cpu className="w-3 h-3 mr-2" />
            Local
          </TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="h-4 w-[1px] bg-border" />

      <Select value={model} onValueChange={onModelChange} disabled={disabled}>
        <SelectTrigger className="h-8 w-[180px] text-xs border-none shadow-none focus:ring-0 bg-transparent">
          <SelectValue placeholder="Select Model" />
        </SelectTrigger>
        <SelectContent>
          {MODEL_OPTIONS[preference].map((opt) => (
            <SelectItem key={opt.value} value={opt.value} className="text-xs">
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
