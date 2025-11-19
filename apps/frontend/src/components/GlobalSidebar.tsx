import { useState } from 'react'
import {
  PanelLeft,
  Plus,
  Settings,
  Trash2,
  Edit2,
  Check,
  X,
  LayoutDashboard,
  LogOut,
  User as UserIcon,
  MoreHorizontal,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useUIStore } from '@/stores/uiStore'
import { useUserStore } from '@/stores/userStore'
import {
  useSessions,
  useDeleteSession,
  useUpdateSession,
} from '@/features/chat/hooks/useSessions'
import { cn } from '@/lib/utils'
import { useNavigate, useLocation } from 'react-router-dom'

export function GlobalSidebar() {
  const {
    isSidebarOpen,
    toggleSidebar,
    currentSessionId,
    setCurrentSessionId,
  } = useUIStore()
  const user = useUserStore((state) => state.user)

  const { data: sessions, isLoading } = useSessions()
  const deleteSession = useDeleteSession()
  const updateSession = useUpdateSession()

  const navigate = useNavigate()
  const location = useLocation()

  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')

  // Navigation Helper
  const handleNavigation = (path: string) => {
    navigate(path)
  }

  // Session Selection
  const handleSelectSession = (sessionId: string | null) => {
    setCurrentSessionId(sessionId)
    navigate('/chat')
  }

  const handleStartEdit = (sessionId: string, currentTitle: string) => {
    setEditingId(sessionId)
    setEditTitle(currentTitle)
  }

  const handleSaveEdit = async (sessionId: string) => {
    if (editTitle.trim()) {
      await updateSession.mutateAsync({
        sessionId,
        data: { title: editTitle.trim() },
      })
    }
    setEditingId(null)
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditTitle('')
  }

  const handleDelete = async (sessionId: string) => {
    await deleteSession.mutateAsync(sessionId)
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null)
    }
  }

  const handleLogout = () => {
    // Add your logout logic here (clear tokens, zustand store, etc)
    if (logout) logout()
    navigate('/login') // or wherever
  }

  // --- Render Collapsed State ---
  if (!isSidebarOpen) {
    return (
      <div className="flex h-full w-12 flex-col items-center border-r bg-muted/30 py-4 transition-all duration-300">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          title="Expand Sidebar"
        >
          <PanelLeft className="h-5 w-5" />
        </Button>

        <div className="mt-4 flex flex-col gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleNavigation('/dashboard')}
            title="Dashboard"
          >
            <LayoutDashboard className="h-5 w-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleSelectSession(null)}
            title="New Chat"
          >
            <Plus className="h-5 w-5" />
          </Button>
        </div>

        <div className="mt-auto">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <UserIcon className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent side="right" align="end" className="w-56">
              <DropdownMenuItem onClick={() => navigate('/profile')}>
                <UserIcon className="mr-2 h-4 w-4" /> Profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/settings')}>
                <Settings className="mr-2 h-4 w-4" /> Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleLogout}
                className="text-destructive"
              >
                <LogOut className="mr-2 h-4 w-4" /> Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    )
  }

  // --- Render Open State ---
  return (
    <div className="flex h-full w-64 flex-col border-r bg-muted/30 transition-all duration-300">
      {/* Header - Clickable to Home */}
      <div className="flex items-center justify-between border-b p-4">
        <h2
          className="text-lg font-semibold tracking-tight cursor-pointer hover:opacity-80 transition-opacity select-none"
          onClick={() => navigate('/')}
        >
          SofIA
        </h2>
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          title="Close sidebar"
        >
          <PanelLeft className="h-5 w-5" />
        </Button>
      </div>

      {/* Primary Actions */}
      <div className="p-2 space-y-1">
        <Button
          className={cn(
            'w-full justify-start',
            location.pathname === '/dashboard' && 'bg-accent'
          )}
          variant="ghost"
          onClick={() => handleNavigation('/dashboard')}
        >
          <LayoutDashboard className="mr-2 h-4 w-4" />
          Dashboard
        </Button>
        <Button
          className="w-full justify-start"
          variant={
            location.pathname === '/chat' && !currentSessionId
              ? 'secondary'
              : 'outline'
          }
          onClick={() => handleSelectSession(null)}
        >
          <Plus className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      </div>

      {/* Chat History */}
      <div className="px-4 pt-2 pb-1 text-xs font-semibold text-muted-foreground">
        Recent Chats
      </div>

      <ScrollArea className="flex-1 px-2">
        {isLoading ? (
          <div className="space-y-2 py-2">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-9 w-full" />
            ))}
          </div>
        ) : sessions && sessions.length > 0 ? (
          <div className="space-y-1 py-1">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={cn(
                  'group relative rounded-md transition-colors',
                  currentSessionId === session.id &&
                    location.pathname === '/chat'
                    ? 'bg-accent text-accent-foreground'
                    : 'hover:bg-accent/50 text-muted-foreground hover:text-foreground'
                )}
              >
                {editingId === session.id ? (
                  <div className="flex items-center gap-1 p-1">
                    <Input
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="h-7 text-xs px-2"
                      autoFocus
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveEdit(session.id)
                        if (e.key === 'Escape') handleCancelEdit()
                      }}
                    />
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-7 w-7 shrink-0"
                      onClick={() => handleSaveEdit(session.id)}
                    >
                      <Check className="h-3 w-3" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-7 w-7 shrink-0"
                      onClick={handleCancelEdit}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => handleSelectSession(session.id)}
                      className="w-full truncate p-2 text-left text-sm"
                    >
                      <span className="truncate block">{session.title}</span>
                    </button>

                    <div className="absolute right-1 top-1 hidden gap-0.5 group-hover:flex bg-muted/80 rounded-sm backdrop-blur-sm">
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-7 w-7"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleStartEdit(session.id, session.title)
                        }}
                      >
                        <Edit2 className="h-3 w-3" />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-7 w-7 text-destructive hover:text-destructive"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(session.id)
                        }}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-muted-foreground">
            No history.
          </div>
        )}
      </ScrollArea>

      {/* Footer - User Dropdown */}
      <div className="border-t p-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="w-full justify-start px-2">
              <div className="flex items-center gap-2 truncate">
                <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <UserIcon className="h-4 w-4 text-primary" />
                </div>
                <span className="truncate">{user?.name || 'User'}</span>
                <MoreHorizontal className="ml-auto h-4 w-4 text-muted-foreground" />
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56" side="right">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => navigate('/profile')}>
              <UserIcon className="mr-2 h-4 w-4" /> Profile
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => navigate('/settings')}>
              <Settings className="mr-2 h-4 w-4" /> Settings
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
