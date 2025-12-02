import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Separator } from "../components/ui/separator";
import { Calendar, Mail, Phone, User } from "lucide-react";

const Profile = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Perfil</h1>
          <p className="text-muted-foreground">
            Gerencie suas informações pessoais e preferências de conta.
          </p>
        </div>

        <Separator />

        <Card className="p-6">
          <div className="flex items-center gap-6 mb-8">
            <Avatar className="w-24 h-24">
              <AvatarImage src="/placeholder-user.jpg" />
              <AvatarFallback className="text-2xl">
                <User className="w-12 h-12" />
              </AvatarFallback>
            </Avatar>
            <div className="space-y-2">
              <h2 className="text-2xl font-semibold">Usuário SofIA</h2>
              <p className="text-muted-foreground">Membro desde Janeiro 2024</p>
            </div>
          </div>

          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName" className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Nome
                </Label>
                <Input id="firstName" placeholder="Seu nome" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName" className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Sobrenome
                </Label>
                <Input id="lastName" placeholder="Seu sobrenome" />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="flex items-center gap-2">
                <Mail className="w-4 h-4" />
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="seu.email@exemplo.com"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone" className="flex items-center gap-2">
                <Phone className="w-4 h-4" />
                Telefone
              </Label>
              <Input id="phone" type="tel" placeholder="(00) 00000-0000" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="birthdate" className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Data de Nascimento
              </Label>
              <Input 
              id="birthdate" 
              type="date" 
              />
            </div>
          </div>

          <Separator className="my-6" />

          <div className="flex justify-end gap-3">
            <Button variant="outline">Cancelar</Button>
            <Button>Salvar Alterações</Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
