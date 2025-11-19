import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useUIStore } from '@/stores/uiStore'
import { useCreateUser } from '@/features/chat/hooks/useUser'
import { Key, User } from 'lucide-react'

const formSchema = z.object({
  name: z.string().min(2, 'O nome deve ter pelo menos 2 caracteres'),
  api_key: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

export function OnboardingModal() {
  const { activeModal, closeModal } = useUIStore()
  const { mutate: createUser, isPending } = useCreateUser()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      api_key: '',
    },
  })

  const onSubmit = (data: FormData) => {
    createUser(
      {
        name: data.name,
        api_key: data.api_key || undefined,
      },
      {
        onSuccess: () => {
          closeModal()
        },
      }
    )
  }
  const handleOpenChange = (open: boolean) => {
    if (!open && activeModal !== 'onboarding') {
      closeModal()
    }
  }
  return (
    <Dialog open={activeModal === 'onboarding'} onOpenChange={handleOpenChange}>
      <DialogContent
        className="sm:max-w-[425px]"
        onInteractOutside={(e) => e.preventDefault()}
      >
        <DialogHeader>
          <DialogTitle>Bem-vindo ao SoFiA</DialogTitle>
          <DialogDescription>
            Para começar, precisamos saber como te chamar. Opcionalmente, insira
            sua chave de API.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 py-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="flex items-center gap-2">
              <User className="w-4 h-4" />
              Seu Nome
            </Label>
            <Input
              id="name"
              placeholder="Como gostaria de ser chamado?"
              {...register('name')}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="api_key" className="flex items-center gap-2">
              <Key className="w-4 h-4" />
              Chave de API (Opcional)
            </Label>
            <Input
              id="api_key"
              type="password"
              placeholder="sk-..."
              {...register('api_key')}
            />
            <p className="text-xs text-muted-foreground">
              Você pode configurar isso mais tarde nos ajustes.
            </p>
          </div>

          <DialogFooter>
            <Button type="submit" disabled={isPending} className="w-full">
              {isPending ? 'Criando perfil...' : 'Começar a usar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
