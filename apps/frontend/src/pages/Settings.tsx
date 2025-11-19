import { useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { Palette, Globe, Key, Save } from 'lucide-react'
import { useUserStore } from '@/stores/userStore'
import { useUpdateUser } from '@/features/chat/hooks/useUser'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'

const settingsSchema = z.object({
  api_key: z.string().optional(),
})

type SettingsFormData = z.infer<typeof settingsSchema>

const Settings = () => {
  const { user } = useUserStore()
  const { mutate: updateUser, isPending } = useUpdateUser()
  const {
    register,
    handleSubmit,
    reset,
    formState: { isDirty },
  } = useForm<SettingsFormData>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      api_key: user?.api_key || '',
    },
  })
  useEffect(() => {
    if (user) {
      reset({ api_key: user.api_key || '' })
    }
  }, [user, reset])
  const onSubmit = (data: SettingsFormData) => {
    if (!user?.id) return
    updateUser(
      { api_key: data.api_key },
      {
        onSuccess: () => {
          toast.success('Chave de API atualizada com sucesso!')
        },
        onError: () => {
          toast.error('Erro ao atualizar chave de API')
        },
      }
    )
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Ajustes</h1>
          <p className="text-muted-foreground">
            Configure suas preferências e chaves de acesso.
          </p>
        </div>

        <Separator />

        {/* API Configuration Card */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Key className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Configuração de API</h2>
              <p className="text-sm text-muted-foreground">
                Gerencie sua chave de conexão com o modelo de IA
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Label htmlFor="api-key">Chave de API</Label>
              <div className="flex gap-3 mt-2">
                <Input
                  id="api-key"
                  type="password"
                  placeholder="sk-..."
                  className="font-mono"
                  {...register('api_key')}
                />
                <Button type="submit" disabled={isPending || !isDirty}>
                  {isPending ? (
                    'Salvando...'
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Salvar
                    </>
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Sua chave é armazenada de forma segura e usada apenas para
                comunicar com o serviço de IA.
              </p>
            </div>
          </form>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Palette className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Aparência</h2>
              <p className="text-sm text-muted-foreground">
                Personalize a interface do aplicativo
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Modo Escuro</Label>
              <p className="text-sm text-muted-foreground">
                Ative o tema escuro
              </p>
            </div>
            <Switch />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Globe className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Idioma e Região</h2>
              <p className="text-sm text-muted-foreground">
                Configure preferências regionais
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <Label htmlFor="language">Idioma</Label>
              <Input
                id="language"
                value="Português (Brasil)"
                disabled
                className="mt-2"
              />
            </div>
            <div>
              <Label htmlFor="currency">Moeda</Label>
              <Input id="currency" value="BRL (R$)" disabled className="mt-2" />
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Settings
