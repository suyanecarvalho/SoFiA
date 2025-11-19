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
  User as UserIcon,
  MoreHorizontal,
  MessageSquare,
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
import { useNavigate, useLocation, useParams } from 'react-router-dom'

export function GlobalSidebar() {
  const { isSidebarOpen, toggleSidebar } = useUIStore()
  const user = useUserStore((state) => state.user)

  // FIX: Get currentSessionId from URL params, not store
  const { sessionId: currentSessionId } = useParams<{ sessionId: string }>()

  const { data: sessions, isLoading } = useSessions()
  const deleteSession = useDeleteSession()
  const updateSession = useUpdateSession()

  const navigate = useNavigate()
  const location = useLocation()

  // State for inline editing
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTitle, setEditTitle] = useState('')

  const handleNavigation = (path: string) => {
    navigate(path)
  }

  // FIX: Navigate to specific ID or new chat
  const handleSelectSession = (sessionId: number | null) => {
    if (sessionId) {
      navigate(`/chat/${sessionId}`)
    } else {
      navigate('/chat')
    }
  }

  const handleStartEdit = (sessionId: number, currentTitle: string) => {
    setEditingId(sessionId)
    setEditTitle(currentTitle)
  }

  const handleSaveEdit = async (sessionId: number) => {
    if (editTitle.trim()) {
      await updateSession.mutateAsync({
        sessionId: sessionId.toString(),
        data: { title: editTitle.trim() },
      })
    }
    setEditingId(null)
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditTitle('')
  }

  const handleDelete = async (sessionId: number) => {
    // Prevent editing if we delete the item being edited
    if (editingId === sessionId) handleCancelEdit()

    await deleteSession.mutateAsync(sessionId.toString())

    // If we deleted the active chat, go to new chat
    if (currentSessionId === sessionId.toString()) {
      navigate('/chat')
    }
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
            className={cn(
              location.pathname === '/dashboard' &&
                'bg-accent text-accent-foreground'
            )}
            title="Dashboard"
          >
            <LayoutDashboard className="h-5 w-5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleSelectSession(null)}
            className={cn(
              location.pathname.includes('/chat') &&
                'bg-accent text-accent-foreground'
            )}
            title="Chat"
          >
            <MessageSquare className="h-5 w-5" />
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
      <div className="flex items-center justify-between border-b p-4 h-[60px]">
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
          className="h-8 w-8"
        >
          <PanelLeft className="h-4 w-4" />
        </Button>
      </div>

      {/* Primary Actions */}
      <div className="p-2 space-y-1">
        <Button
          className={cn(
            'w-full justify-start',
            location.pathname === '/dashboard' &&
              'bg-accent text-accent-foreground'
          )}
          variant="ghost"
          onClick={() => handleNavigation('/dashboard')}
        >
          <LayoutDashboard className="mr-2 h-4 w-4" />
          Dashboard
        </Button>
        <Button
          className={cn(
            'w-full justify-start',
            location.pathname === '/chat' &&
              !currentSessionId &&
              'bg-accent text-accent-foreground'
          )}
          variant="ghost"
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
            {sessions.map((session) => {
              // Determine if this session is active based on URL
              const isActive = currentSessionId === session.id.toString()

              return (
                <div
                  key={session.id}
                  className={cn(
                    'group relative rounded-md transition-colors',
                    isActive
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
                        className="w-full truncate p-2 text-left text-sm pr-8"
                      >
                        <span className="truncate block">
                          {session.title || 'Untitled Chat'}
                        </span>
                      </button>

                      <div className="absolute right-1 top-1 hidden gap-0.5 group-hover:flex bg-muted/80 rounded-sm backdrop-blur-sm shadow-sm">
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7 hover:bg-background"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleStartEdit(session.id, session.title || '')
                          }}
                        >
                          <Edit2 className="h-3 w-3" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7 text-destructive hover:text-destructive hover:bg-background"
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
              )
            })}
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-muted-foreground">
            No history.
          </div>
        )}
      </ScrollArea>

      {/* Footer - User Dropdown */}
      <div className="border-t p-2 bg-background">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="w-full justify-start px-2 h-12">
              <div className="flex items-center gap-2 w-full">
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 border">
                  {user?.profile_pic ? (
                    <img
                      src={user.profile_pic}
                      alt="User"
                      className="h-full w-full rounded-full object-cover"
                    />
                  ) : (
                    <UserIcon className="h-4 w-4 text-primary" />
                  )}
                </div>
                <div className="flex flex-col items-start overflow-hidden">
                  <span className="truncate text-sm font-medium w-full text-left">
                    {user?.name || 'User'}
                  </span>
                  <span className="truncate text-xs text-muted-foreground w-full text-left">
                    Free Plan
                  </span>
                </div>
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
