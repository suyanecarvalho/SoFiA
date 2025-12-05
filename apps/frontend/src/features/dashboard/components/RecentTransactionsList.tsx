import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import TransactionItem from '@/components/TransactionItem'
import type { Transaction } from '../types'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'

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

  const recentTransactions = data?.slice(0, 5) ?? []
  const allTransactions = data ?? []

  const renderTransactionItem = (t: Transaction) => (
    <TransactionItem
      key={t.id}
      icon={
        getIcon(
          t.category_id,
          t.transaction_type
        ) as any
      }
      title={t.description}
      category={
        t.transaction_type === 'income' ? 'Receita' : 'Despesa'
      }
      amount={t.amount}
      date={new Date(t.reference_date || '').toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: 'short',
      })}
      type={t.transaction_type}
    />
  )

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className='flex justify-between w-full'>
          Registro
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm" className="text-primary hover:text-primary/80">
                Ver todas
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-3xl max-h-[85vh]">
              <DialogHeader>
                <DialogTitle className="text-2xl">Todas as Transações</DialogTitle>
              </DialogHeader>
              <ScrollArea className="h-[65vh] pr-4">
                <div className="space-y-0">
                  {allTransactions.length === 0 ? (
                    <p className="text-muted-foreground text-sm py-4">
                      Nenhuma transação encontrada.
                    </p>
                  ) : (
                    allTransactions.map(renderTransactionItem)
                  )}
                </div>
              </ScrollArea>
            </DialogContent>
          </Dialog>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-0">
          {recentTransactions.length === 0 ? (
            <p className="text-muted-foreground text-sm py-4">
              Nenhuma transação encontrada.
            </p>
          ) : (
            recentTransactions.map(renderTransactionItem)
          )}
        </div>
      </CardContent>
    </Card>
  )
}
