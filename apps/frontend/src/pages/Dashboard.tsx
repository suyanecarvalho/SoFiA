import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  Target,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
} from 'lucide-react'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts'
import { useNavigate } from 'react-router-dom'

const Dashboard = () => {
  const navigate = useNavigate()

  const currentBalance = 4250.8
  const monthlyIncome = 7500.0
  const monthlyExpenses = 3249.2
  const savingsRate = (
    ((monthlyIncome - monthlyExpenses) / monthlyIncome) *
    100
  ).toFixed(1)

  const expensesByCategory = [
    {
      category: 'Alimentação',
      amount: 850.5,
      percentage: 26,
      color: 'hsl(var(--chart-1))',
    },
    {
      category: 'Transporte',
      amount: 620.3,
      percentage: 19,
      color: 'hsl(var(--chart-2))',
    },
    {
      category: 'Moradia',
      amount: 1200.0,
      percentage: 37,
      color: 'hsl(var(--chart-3))',
    },
    {
      category: 'Lazer',
      amount: 378.4,
      percentage: 12,
      color: 'hsl(var(--chart-4))',
    },
    {
      category: 'Outros',
      amount: 200.0,
      percentage: 6,
      color: 'hsl(var(--chart-5))',
    },
  ]

  const monthlyTrend = [
    { month: 'Jan', receitas: 7200, despesas: 3100 },
    { month: 'Fev', receitas: 7400, despesas: 3300 },
    { month: 'Mar', receitas: 7100, despesas: 2900 },
    { month: 'Abr', receitas: 7600, despesas: 3400 },
    { month: 'Mai', receitas: 7500, despesas: 3249 },
  ]

  const recentTransactions = [
    {
      id: 1,
      description: 'Supermercado Extra',
      amount: -125.5,
      category: 'Alimentação',
      date: '18/05',
    },
    {
      id: 2,
      description: 'Salário',
      amount: 7500.0,
      category: 'Receita',
      date: '15/05',
    },
    {
      id: 3,
      description: 'Uber',
      amount: -32.8,
      category: 'Transporte',
      date: '17/05',
    },
    {
      id: 4,
      description: 'Netflix',
      amount: -49.9,
      category: 'Lazer',
      date: '16/05',
    },
  ]

  const savingsGoals = [
    { name: 'Viagem de Férias', current: 2400, target: 5000, progress: 48 },
    { name: 'Fundo de Emergência', current: 8500, target: 15000, progress: 57 },
  ]

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground">
            Visão geral das suas finanças em tempo real
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="w-4 h-4" />
          Nova Transação
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Wallet className="w-5 h-5 text-primary" />
            </div>
            <Badge variant="secondary" className="gap-1">
              <Calendar className="w-3 h-3" />
              Maio
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mb-1">Saldo Atual</p>
          <p className="text-2xl font-bold">R$ {currentBalance.toFixed(2)}</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <ArrowUpRight className="w-4 h-4 text-green-600 dark:text-green-400" />
          </div>
          <p className="text-sm text-muted-foreground mb-1">Receitas</p>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
            R$ {monthlyIncome.toFixed(2)}
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center">
              <TrendingDown className="w-5 h-5 text-red-600 dark:text-red-400" />
            </div>
            <ArrowDownRight className="w-4 h-4 text-red-600 dark:text-red-400" />
          </div>
          <p className="text-sm text-muted-foreground mb-1">Despesas</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">
            R$ {monthlyExpenses.toFixed(2)}
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Target className="w-5 h-5 text-primary" />
            </div>
            <Badge variant="default">{savingsRate}%</Badge>
          </div>
          <p className="text-sm text-muted-foreground mb-1">Taxa de Economia</p>
          <p className="text-2xl font-bold">
            R$ {(monthlyIncome - monthlyExpenses).toFixed(2)}
          </p>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Expenses by Category */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-6">Despesas por Categoria</h2>
          <ChartContainer
            config={{
              amount: {
                label: 'Valor',
                color: 'hsl(var(--chart-1))',
              },
            }}
            className="h-[300px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={expensesByCategory}>
                <XAxis
                  dataKey="category"
                  tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `R$ ${value}`}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar
                  dataKey="amount"
                  fill="hsl(var(--primary))"
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </Card>

        {/* Monthly Trend */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-6">Tendência Mensal</h2>
          <ChartContainer
            config={{
              receitas: {
                label: 'Receitas',
                color: 'hsl(var(--chart-2))',
              },
              despesas: {
                label: 'Despesas',
                color: 'hsl(var(--chart-1))',
              },
            }}
            className="h-[300px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyTrend}>
                <XAxis
                  dataKey="month"
                  tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `R$ ${value}`}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Line
                  type="monotone"
                  dataKey="receitas"
                  stroke="hsl(var(--chart-2))"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="despesas"
                  stroke="hsl(var(--chart-1))"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Transactions */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Transações Recentes</h2>
            <Button variant="ghost" size="sm">
              Ver Todas
            </Button>
          </div>
          <div className="space-y-4">
            {recentTransactions.map((transaction) => (
              <div
                key={transaction.id}
                className="flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      transaction.amount > 0
                        ? 'bg-green-500/10'
                        : 'bg-red-500/10'
                    }`}
                  >
                    {transaction.amount > 0 ? (
                      <ArrowUpRight className="w-5 h-5 text-green-600 dark:text-green-400" />
                    ) : (
                      <ArrowDownRight className="w-5 h-5 text-red-600 dark:text-red-400" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-sm">
                      {transaction.description}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {transaction.category} · {transaction.date}
                    </p>
                  </div>
                </div>
                <p
                  className={`font-semibold ${
                    transaction.amount > 0
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-red-600 dark:text-red-400'
                  }`}
                >
                  {transaction.amount > 0 ? '+' : ''}R${' '}
                  {Math.abs(transaction.amount).toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </Card>

        {/* Savings Goals */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Metas de Economia</h2>
            <Button variant="ghost" size="sm" onClick={() => navigate('/chat')}>
              Criar Meta
            </Button>
          </div>
          <div className="space-y-6">
            {savingsGoals.map((goal, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{goal.name}</span>
                  <span className="text-muted-foreground">
                    R$ {goal.current} / R$ {goal.target}
                  </span>
                </div>
                <div className="relative h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="absolute inset-y-0 left-0 bg-primary rounded-full transition-all"
                    style={{ width: `${goal.progress}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{goal.progress}% completo</span>
                  <span>
                    Faltam R$ {(goal.target - goal.current).toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard
