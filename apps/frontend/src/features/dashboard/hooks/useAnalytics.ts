import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { analyticsService } from '../services/analyticsService'

export function useDashboardSummary(month: number, year: number) {
  return useQuery({
    queryKey: ['dashboard-summary', month, year],
    queryFn: () => analyticsService.getSummary(month, year),
    placeholderData: keepPreviousData,
  })
}

export function useCategorySpending(month: number, year: number) {
  return useQuery({
    queryKey: ['dashboard-categories', month, year],
    queryFn: () => analyticsService.getCategorySpending(month, year),
    placeholderData: keepPreviousData,
  })
}

export function useMonthlyEvolution(months: number = 6) {
  return useQuery({
    queryKey: ['dashboard-evolution', months],
    queryFn: () => analyticsService.getMonthlyEvolution(months),
    staleTime: 1000 * 60 * 10, // Charts don't change often, cache for 10m
  })
}

export function useRecentTransactions(limit: number = 5) {
  return useQuery({
    queryKey: ['recent-transactions', limit],
    queryFn: () => analyticsService.getRecentTransactions(limit),
  })
}
