import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import MetricCard from "../components/MetricCard";
import TransactionItem from "../components/TransactionItem";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "../components/ui/chart";
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from "recharts";
import { Button } from "../components/ui/button";

const Dashboard = () => {
  const categoryData = [
    { name: "Alimentação", value: 22, color: "#07ad18"},
    { name: "Transporte", value: 16, color: "#14d9c5" },
    { name: "Moradia", value: 37, color: "#9534eb" },
    { name: "Lazer", value: 11, color: "#6823e8" },
    { name: "Saúde", value: 7, color: "#d92b14" },
    { name: "Outros", value: 7, color: "#acacad" },
  ];

  const monthlyData = [
    { month: "Jul", receitas: 7500, despesas: 5200 },
    { month: "Ago", receitas: 8200, despesas: 6100 },
    { month: "Set", receitas: 9100, despesas: 5800 },
    { month: "Out", receitas: 8700, despesas: 5900 },
    { month: "Nov", receitas: 10500, despesas: 6200 },
    { month: "Dez", receitas: 8500, despesas: 4900 },
  ];

  const chartConfig = {
    receitas: {
      label: "Receitas",
      color: "#07ad18",
    },
    despesas: {
      label: "Despesas",
      color: "#d92b14",
    },
  };

  const recentTransactions = [
    {
      id: 1,
      icon: "shopping" as const,
      title: "Supermercado Extra",
      category: "Alimentação",
      amount: 342.50,
      date: "Hoje",
      type: "expense" as const,
    },
    {
      id: 2,
      icon: "income" as const,
      title: "Salário",
      category: "Receita",
      amount: 8500.00,
      date: "Hoje",
      type: "income" as const,
    },
    {
      id: 3,
      icon: "transport" as const,
      title: "Uber",
      category: "Transporte",
      amount: 28.90,
      date: "Ontem",
      type: "expense" as const,
    },
    {
      id: 4,
      icon: "housing" as const,
      title: "Aluguel",
      category: "Moradia",
      amount: 2100.00,
      date: "28 Nov",
      type: "expense" as const,
    },
    {
      id: 5,
      icon: "entertainment" as const,
      title: "Netflix",
      category: "Lazer",
      amount: 55.90,
      date: "27 Nov",
      type: "expense" as const,
    },
    {
      id: 6,
      icon: "health" as const,
      title: "Farmácia",
      category: "Saúde",
      amount: 89.00,
      date: "26 Nov",
      type: "expense" as const,
    },
  ];

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Bem-vindo de volta, Sr. Fulano!</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Saldo Total"
            value="R$ 12.450,00"
            change="+12% este mês"
            trend="up"
            icon="wallet"
          />
          <MetricCard
            title="Receitas"
            value="R$ 8.500,00"
            change="+8% vs mês anterior"
            trend="up"
            icon="income"
          />
          <MetricCard
            title="Despesas"
            value="R$ 5.690,00"
            change="-3% vs mês anterior"
            trend="down"
            icon="expense"
          />
          <MetricCard
            title="Economia"
            value="R$ 2.810,00"
            change="33% da receita"
            trend="neutral"
            icon="savings"
          />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Gastos por Categoria</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <ChartTooltip content={<ChartTooltipContent />} />
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
            <div className="grid grid-cols-2 gap-3 mt-6">
              {categoryData.map((category, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: category.color }}
                  />
                  <span className="text-sm text-foreground">{category.name}</span>
                  <span className="text-sm font-semibold text-foreground ml-auto">
                    {category.value}%
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Evolução Mensal</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="month"
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                  />
                  <YAxis
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                    tickFormatter={(value) => `${value / 1000}k`}
                  />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                  <Bar dataKey="receitas" fill="#07ad18" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="despesas" fill="#d92b14" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Transações Recentes</CardTitle>
            <Button variant="ghost" size="sm" className="text-primary hover:text-primary/80">
              Ver todas
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-0">
              {recentTransactions.map((transaction) => (
                <TransactionItem
                  key={transaction.id}
                  icon={transaction.icon}
                  title={transaction.title}
                  category={transaction.category}
                  amount={transaction.amount}
                  date={transaction.date}
                  type={transaction.type}
                />
              ))}
            </div>
          </CardContent>
        </Card>
    </div>
  );
};

export default Dashboard;