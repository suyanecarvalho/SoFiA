import Button from "../../components/ui/Button/button";
import { House, MessagesSquare, ChartColumnBig, Settings, User, SendHorizonal } from "lucide-react";
import "../../app/globals.css"
import "./style.css"
import TextInput from "../../components/ui/TextInput/textInput";

export default function ChatPage() {
  return (
    <main className="screen">
      <div className="navigationBar">
        <div className="upperButtonsDiv">
            <Button>
                <House />
                <p>Início</p>
            </Button>
            <Button>
                <MessagesSquare />
                <p>Chat</p>
            </Button>
            <Button>
                <ChartColumnBig />
                <p>Dashboard</p>
            </Button>
        </div>
        <div className="lowerButtonsDiv">
            <Button>
                <Settings />
                <p>Ajustes</p>
            </Button>
            <Button>
                <User />
                <p>Perfil</p>
            </Button>
        </div>
      </div>

      <div className="body">
        <div className="topBar">
            <h1>SofIA</h1>
        </div>
        <div className="restOfBody">
          <div className="utilArea">
            <div className="chatContainer">
                <TextInput>Digite uma mensagem</TextInput>
                <button className="sendButton">
                  <SendHorizonal></SendHorizonal>
                </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};
