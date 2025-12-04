import { NavLink } from "react-router-dom";
import { Home, MessageSquare, LayoutDashboard, Settings, User, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";
import { cn } from "../lib/utils";
import { Button } from "../components/ui/button";

const Layout = ({ children }: { children: React.ReactNode }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <aside className={cn(
        "bg-[#4e6e97] flex flex-col transition-all duration-300" ,
        isCollapsed ? "w-[70px]" : "w-[180px]"
      )}>
        <div className="p-3 flex items-center justify-between border-b border-sidebar-border">
          {!isCollapsed && (
            <span className="text-lg font-bold text-[#e6ebf2]">SofIA</span>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsCollapsed(!isCollapsed)}
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4 text-[#e6ebf2]"/>
            ) : (
              <ChevronLeft className="h-4 w-4 text-[#e6ebf2]"/>
            )}
          </Button>
        </div>

        <nav className="flex-1 px-3 space-y-1 mt-3">
          <NavLink
            to="/"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all",
                isActive
                  ? "bg-[#6186b8] text-[#e6ebf2]"
                  : "text-[#e6ebf2] hover:bg-[#6186b8]/50 hover:text-[#e6ebf2]",
                isCollapsed && "justify-center"
              )
            }
            title={isCollapsed ? "Início" : undefined}
          >
            <Home className="w-5 h-5" />
            {!isCollapsed && "Início"}
          </NavLink>
          
          <NavLink
            to="/chat"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all",
                isActive
                  ? "bg-[#6186b8] text-[#e6ebf2]"
                  : "text-[#e6ebf2] hover:bg-[#6186b8]/50 hover:text-[#e6ebf2]",
                isCollapsed && "justify-center"
              )
            }
            title={isCollapsed ? "Chat" : undefined}
          >
            <MessageSquare className="w-5 h-5" />
            {!isCollapsed && "Chat"}
          </NavLink>
          
          {/*<NavLink
            to="/dashboard"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground",
                isCollapsed && "justify-center"
              )
            }
            title={isCollapsed ? "Dashboard" : undefined}
          >
            <LayoutDashboard className="w-5 h-5" />
            {!isCollapsed && "Dashboard"}
          </NavLink>*/}
        </nav>

        <div className="p-3 space-y-1 border-t border-sidebar-border">
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all",
                isActive
                  ? "bg-[#6186b8] text-[#e6ebf2]"
                  : "text-[#e6ebf2] hover:bg-[#6186b8]/50 hover:text-[#e6ebf2]",
                isCollapsed && "justify-center"
              )
            }
            title={isCollapsed ? "Ajustes" : undefined}
          >
            <Settings className="w-5 h-5" />
            {!isCollapsed && "Ajustes"}
          </NavLink>
          
          {/*<NavLink
            to="/profile"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all",
                isActive
                  ? "bg-[#6186b8] text-[#e6ebf2]"
                  : "text-[#e6ebf2] hover:bg-[#6186b8]/50 hover:text-[#e6ebf2]",
                isCollapsed && "justify-center"
              )
            }
            title={isCollapsed ? "Perfil" : undefined}
          >
            <User className="w-5 h-5" />
            {!isCollapsed && "Perfil"}
          </NavLink>*/}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
};

export default Layout;