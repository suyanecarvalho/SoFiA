import type { UseFormReturn } from 'react-hook-form'
import type { User } from '@/features/chat/types'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Key, User as UserIcon, Calendar, Loader2, DollarSign } from 'lucide-react'
import type { ProfileFormValues } from '@/features/profile/types'

interface ProfileFormProps {
  form: UseFormReturn<ProfileFormValues>
  onSubmit: () => void
  isPending: boolean
  user: User
  memberSince: string
}

export function ProfileForm({
  form,
  onSubmit,
  isPending,
  user,
  memberSince,
}: ProfileFormProps) {
  const {
    register,
    formState: { errors, isDirty },
  } = form

  return (
    <Card className="p-6">
      <form onSubmit={onSubmit}>
        <div className="flex flex-col md:flex-row items-center gap-6 mb-8">
          <Avatar className="w-24 h-24 border-2 border-border">
            <AvatarImage src={user.profile_pic || undefined} />
            <AvatarFallback className="text-2xl bg-muted">
              <UserIcon className="w-10 h-10 text-muted-foreground" />
            </AvatarFallback>
          </Avatar>
          <div className="space-y-2 text-center md:text-left">
            <h2 className="text-2xl font-semibold">{user.name}</h2>
            <div className="flex items-center justify-center md:justify-start gap-2 text-muted-foreground">
              <Calendar className="w-4 h-4" />
              <span className="text-sm">Membro desde {memberSince}</span>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name" className="flex items-center gap-2">
              <UserIcon className="w-4 h-4" />
              Nome Completo
            </Label>
            <Input
              id="name"
              placeholder="Seu nome"
              {...register('name')}
              disabled={isPending}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="api_key" className="flex items-center gap-2">
              <Key className="w-4 h-4" />
              Chave de API do Gemini
            </Label>
            <Input
              id="api_key"
              type="password"
              placeholder="sk-..."
              {...register('api_key')}
              disabled={isPending}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="salary" className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Salário Mensal
            </Label>
            <Input
              id="salary"
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              placeholder="Ex: 5000"
              {...register('salary')}
              disabled={isPending}
            />
            {errors.salary && (
              <p className="text-sm text-destructive">{errors.salary.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="payday" className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Dia de Recebimento
            </Label>
            <Input
              id="payday"
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              placeholder="Ex: 5"
              {...register('payday')}
              disabled={isPending}
            />
            {errors.payday && (
              <p className="text-sm text-destructive">{errors.payday.message}</p>
            )}
          </div>
        </div>

        <Separator className="my-6" />

        <div className="flex justify-end gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => form.reset()}
            disabled={isPending || !isDirty}
          >
            Descartar
          </Button>
          <Button type="submit" disabled={isPending}>
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Salvar Alterações
          </Button>
        </div>
      </form>
    </Card>
  )
}
