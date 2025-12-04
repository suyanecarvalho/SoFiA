import { useMutation, useQueryClient } from '@tanstack/react-query'
import { userService } from '../../auth/services/userService.ts'
import { useUserStore } from '@/stores/userStore'
import type { CreateUserRequest, UpdateUserRequest } from '../types'

export function useCreateUser() {
  const setUser = useUserStore((state) => state.setUser)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateUserRequest) => userService.createUser(data),
    onSuccess: (user) => {
      setUser(user)
      queryClient.setQueryData(['me'], user)
    },
  })
}

export function useUpdateUser() {
  const { user, setUser } = useUserStore()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: UpdateUserRequest) => {
      if (!user?.id) throw new Error('No user ID found')
      return userService.updateUser(user.id.toString(), data)
    },
    onSuccess: (updatedUser) => {
      setUser(updatedUser)
      queryClient.setQueryData(['me'], updatedUser)
    },
  })
}
