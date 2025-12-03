import { useMutation } from '@tanstack/react-query'
import { userService } from '../../auth/services/userService.ts'
import { useUserStore } from '@/stores/userStore'
import type { CreateUserRequest, UpdateUserRequest } from '../types'

export function useCreateUser() {
  const setUser = useUserStore((state) => state.setUser)

  return useMutation({
    mutationFn: (data: CreateUserRequest) => userService.createUser(data),
    onSuccess: (user) => {
      setUser(user)
    },
  })
}

export function useUpdateUser() {
  const { user, setUser } = useUserStore()

  return useMutation({
    mutationFn: (data: UpdateUserRequest) => {
      if (!user?.id) throw new Error('No user ID found')
      return userService.updateUser(user.id, data)
    },
    onSuccess: (updatedUser) => {
      setUser(updatedUser)
    },
  })
}
