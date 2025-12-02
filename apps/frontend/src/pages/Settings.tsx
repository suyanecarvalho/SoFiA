import { Card } from "../components/ui/card";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";
import { Palette } from "lucide-react";
import { Separator } from "../components/ui/separator";

const Settings = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Ajustes</h1>
          <p className="text-muted-foreground">Configure suas preferências e ajustes.</p>
        </div>

        <Separator />

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Palette className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Aparência</h2>
              <p className="text-sm text-muted-foreground">
                Personalize a interface do aplicativo
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Modo Escuro</Label>
              <p className="text-sm text-muted-foreground">
                Ative o tema escuro
              </p>
            </div>
            <Switch />
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Settings;
