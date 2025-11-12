import { useState } from "react";
import { Send } from "lucide-react";
import SuggestionCard from "../components/SuggestionCard";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

const Chat = () => {
  const [message, setMessage] = useState("");

  const suggestions = [
    "Criar meta Viagem R$ 300/mês",
    "Quanto gastei em transporte este mês?",
    "Adicionar gasto com alimentação",
    "Como economizar 100 reais por semana?",
  ];

  const handleSendMessage = () => {
    if (message.trim()) {
      // Handle message sending logic here
      console.log("Sending:", message);
      setMessage("");
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setMessage(suggestion);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="px-8 py-6 border-b">
        <h1 className="text-xl font-semibold">SofIA</h1>
      </header>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 pb-32">
        <div className="w-full max-w-3xl space-y-8">
          <h2 className="text-4xl font-bold text-center text-foreground">
            Como posso lhe ajudar?
          </h2>

          <div>
            <h3 className="text-lg font-semibold mb-4 text-foreground">
              Sugestões rápidas
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {suggestions.map((suggestion, index) => (
                <SuggestionCard
                  key={index}
                  text={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="px-8 pb-8">
        <div className="max-w-3xl mx-auto space-y-2">
          <div className="relative">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Digite uma mensagem"
              className="pr-12 py-6 rounded-full border-2 focus-visible:ring-primary"
            />
            <Button
              onClick={handleSendMessage}
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full h-9 w-9"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <p className="text-xs text-center text-muted-foreground">
            Utilizando modelo XXX
          </p>
        </div>
      </div>
    </div>
  );
};

export default Chat;
