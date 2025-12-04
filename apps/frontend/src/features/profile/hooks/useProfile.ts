import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
import { useUserStore } from '@/stores/userStore'
import { useUpdateUser } from '@/features/auth/hooks/useUser.ts'
import { type ProfileFormValues, profileSchema } from '@/features/profile/types'

export function useProfile() {
  const user = useUserStore((state) => state.user)
  const { mutate: updateUser, isPending } = useUpdateUser()

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: '',
      api_key: '',
      profile_pic: '',
      salary: '',
      payday: '',
    },
  })

  useEffect(() => {
    if (user) {
      form.reset({
        name: user.name || '',
        api_key: user.api_key || '',
        profile_pic: user.profile_pic || '',
        salary: user.salary?.toString() || '',
        payday: user.payday?.toString() || '',
      })
    }
  }, [user, form])

  const handleSubmit = (data: ProfileFormValues) => {
    const salaryValue = data.salary && data.salary.trim() !== '' ? parseInt(data.salary) : undefined
    const paydayValue = data.payday && data.payday.trim() !== '' ? parseInt(data.payday) : undefined
    
    updateUser(
      {
        name: data.name,
        api_key: data.api_key || undefined,
        profile_pic: data.profile_pic || undefined,
        salary: salaryValue,
        payday: paydayValue,
      },
      {
        onSuccess: () => {
          toast.success('Perfil atualizado com sucesso!')
        },
        onError: () => {
          toast.error('Erro ao atualizar perfil.')
        },
      }
    )
  }

  const memberSince = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('pt-BR', {
        month: 'long',
        year: 'numeric',
      })
    : 'Data desconhecida'

  return {
    user,
    form,
    isPending,
    memberSince,
    onSubmit: form.handleSubmit(handleSubmit),
  }
}
