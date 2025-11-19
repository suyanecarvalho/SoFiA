import type { User, CreateUserRequest, UpdateUserRequest } from '../types'
import apiClient from '@/lib/api/api-client'

export const userService = {
  async createUser(payload: CreateUserRequest): Promise<User> {
    const { data } = await apiClient.post<User>('/api/v1/users', payload)
    return data
  },

  async updateUser(userId: string, payload: UpdateUserRequest): Promise<User> {
    const { data } = await apiClient.put<User>(
      `/api/v1/users/${userId}`,
      payload
    )
    return data
  },
}
