import { Button } from '@/components/ui/button'
import { ArrowRight, TrendingUp, Target, PiggyBank } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card } from '@/components/ui/card'

const Home = () => {
  const navigate = useNavigate()

  const features = [
    {
      icon: TrendingUp,
      title: 'Análise Inteligente',
      description: 'Acompanhe seus gastos com insights em tempo real',
    },
    {
      icon: Target,
      title: 'Metas Personalizadas',
      description: 'Defina e alcance seus objetivos financeiros',
    },
    {
      icon: PiggyBank,
      title: 'Economia Automática',
      description: 'Sugestões inteligentes para economizar mais',
    },
  ]

  return (
    <div className="flex min-h-screen items-center justify-center px-8">
      <div className="text-center max-w-4xl w-full space-y-12">
        <div className="space-y-6">
          <h1 className="text-6xl font-bold text-balance text-foreground">
            Bem-vindo ao SofIA
          </h1>
          <p className="text-xl text-muted-foreground text-balance max-w-2xl mx-auto leading-relaxed">
            Seu assistente financeiro inteligente para gerenciar gastos e
            alcançar suas metas com segurança e praticidade.
          </p>
        </div>

        <div className="flex gap-4 justify-center">
          <Button
            size="lg"
            onClick={() => navigate('/chat')}
            className="gap-2 text-lg h-12 px-8"
          >
            Começar Agora
            <ArrowRight className="w-5 h-5" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate('/dashboard')}
            className="text-lg h-12 px-8"
          >
            Ver Dashboard
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card
                key={index}
                className="p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex flex-col items-center text-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-semibold text-lg">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default Home
