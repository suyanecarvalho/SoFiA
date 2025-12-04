import { Separator } from '@/components/ui/separator'
import { Loader2 } from 'lucide-react'
import { ProfileForm } from '@/features/profile/components/profile-form'
import { useProfile } from '@/features/profile/hooks/useProfile.ts'
import { Label } from '@/components/ui/label.tsx'
import { Switch } from '@/components/ui/switch.tsx'
import { Card } from '@/components/ui/card.tsx'

const Profile = () => {
  const { user, form, onSubmit, isPending, memberSince } = useProfile()
  if (!user) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-4xl mx-auto animate-in fade-in duration-500">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Ajustes</h1>
          <p className="text-muted-foreground">
            Gerencie suas informações pessoais e configurações.
          </p>
        </div>
        <Separator />
        <ProfileForm
          user={user}
          form={form}
          onSubmit={onSubmit}
          isPending={isPending}
          memberSince={memberSince}
        />
        <Card className='p-6'>
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
      </div>
    </div>
  )
}

export default Profile
