import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import TransactionItem from '@/components/TransactionItem'
import type { Transaction } from '../types'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'

interface Props {
  data?: Transaction[]
  isLoading: boolean
}

export function RecentTransactionsList({ data, isLoading }: Props) {
  if (isLoading) {
    return <Skeleton className="h-[300px] w-full rounded-xl" />
  }

  const getIcon = (categoryName: string, type: string) => {
    if (type === 'income') return 'income'
    const cat = categoryName.toLowerCase()
    if (cat.includes('aliment')) return 'shopping'
    if (cat.includes('transport')) return 'transport'
    if (cat.includes('saúde') || cat.includes('saude')) return 'health'
    if (cat.includes('lazer')) return 'entertainment'
    if (cat.includes('moradia')) return 'housing'
    return 'shopping'
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Transações Recentes</CardTitle>
        <Button
          variant="ghost"
          size="sm"
          className="text-primary hover:text-primary/80"
        >
          Ver todas
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-0">
          {data?.length === 0 ? (
            <p className="text-muted-foreground text-sm py-4">
              Nenhuma transação encontrada.
            </p>
          ) : (
            data?.map((t) => (
              <TransactionItem
                key={t.id}
                icon={
                  getIcon(
                    t.category_id ? 'expense' : 'Receita',
                    t.transaction_type
                  ) as any
                }
                title={t.description}
                category={
                  t.transaction_type === 'income' ? 'Receita' : 'Despesa'
                }
                amount={t.amount}
                date={new Date(t.created_at || '').toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: 'short',
                })}
                type={t.transaction_type}
              />
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
