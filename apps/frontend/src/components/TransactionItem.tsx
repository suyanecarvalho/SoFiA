import { ShoppingCart, TrendingUp, Car, Home, Tv, Heart } from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface TransactionItemProps {
  icon: "shopping" | "income" | "transport" | "housing" | "entertainment" | "health";
  title: string;
  category: string;
  amount: number;
  date: string;
  type: "income" | "expense";
}

const iconMap: Record<string, LucideIcon> = {
  shopping: ShoppingCart,
  income: TrendingUp,
  transport: Car,
  housing: Home,
  entertainment: Tv,
  health: Heart,
};

const TransactionItem = ({ icon, title, category, amount, date, type }: TransactionItemProps) => {
  const Icon = iconMap[icon];
  const isIncome = type === "income";

  return (
    <div className="flex items-center justify-between py-4 border-b border-border last:border-0">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
          <Icon className="w-5 h-5 text-muted-foreground" />
        </div>
        <div>
          <p className="font-medium text-foreground">{title}</p>
          <p className="text-sm text-muted-foreground">{category}</p>
        </div>
      </div>
      <div className="text-right">
        <p className={`font-semibold ${isIncome ? "text-[#52c41a]" : "text-[#ff4d4f]"}`}>
          {isIncome ? "+" : "-"}R$ {amount.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
        </p>
        <p className="text-sm text-muted-foreground">{date}</p>
      </div>
    </div>
  );
};

export default TransactionItem;