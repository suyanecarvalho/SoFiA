import { z } from 'zod'

export const profileSchema = z.object({
  name: z.string().min(2, 'O nome deve ter pelo menos 2 caracteres'),
  api_key: z.string().optional().nullable(),
  profile_pic: z.string().optional().nullable(),
})

export type ProfileFormValues = z.infer<typeof profileSchema>
