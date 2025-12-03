'use client';

import { useState } from 'react';
import { PanelLeft, Plus, Settings, Trash2, Edit2, Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { useUIStore } from '@/stores/uiStore';
import { useUserStore } from '@/stores/userStore';
import { useSessions, useDeleteSession, useUpdateSession } from '@/features/chat/hooks/useSessions';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

export function ChatSidebar() {
  const { isSidebarOpen, toggleSidebar, openModal, currentSessionId, setCurrentSessionId } = useUIStore();
  const user = useUserStore((state) => state.user);
  const { data: sessions, isLoading } = useSessions();
  const deleteSession = useDeleteSession();
  const updateSession = useUpdateSession();

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const handleStartEdit = (sessionId: string, currentTitle: string) => {
    setEditingId(sessionId);
    setEditTitle(currentTitle);
  };

  const handleSaveEdit = async (sessionId: string) => {
    if (editTitle.trim()) {
      await updateSession.mutateAsync({ sessionId, data: { title: editTitle.trim() } });
    }
    setEditingId(null);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
  };

  const handleDelete = async (sessionId: string) => {
    await deleteSession.mutateAsync(sessionId);
  };

  if (!isSidebarOpen) {
    return (
      <div className="flex h-full w-12 flex-col items-center border-r bg-muted/30 py-4">
        <Button variant="ghost" size="icon" onClick={toggleSidebar}>
          <PanelLeft className="h-5 w-5" />
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-full w-64 flex-col border-r bg-muted/30">
      <div className="flex items-center justify-between border-b p-4">
        <h2 className="text-lg font-semibold">Chats</h2>
        <Button variant="ghost" size="icon" onClick={toggleSidebar} title="Toggle sidebar">
          <PanelLeft className="h-5 w-5" />
        </Button>
      </div>

      <div className="p-2">
        <Button
          className="w-full"
          onClick={() => setCurrentSessionId(null)}
          title="New chat (Ctrl+Shift+N)"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      </div>

      <ScrollArea className="flex-1 px-2">
        {isLoading ? (
          <div className="space-y-2 py-2">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : sessions && sessions.length > 0 ? (
          <div className="space-y-1 py-2">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={cn(
                  'group relative rounded-md transition-colors',
                  currentSessionId === session.id ? 'bg-accent' : 'hover:bg-accent/50'
                )}
              >
                {editingId === session.id ? (
                  <div className="flex items-center gap-1 p-2">
                    <Input
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="h-8 text-sm"
                      autoFocus
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveEdit(session.id);
                        if (e.key === 'Escape') handleCancelEdit();
                      }}
                    />
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8 shrink-0"
                      onClick={() => handleSaveEdit(session.id)}
                      title="Save"
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-8 w-8 shrink-0"
                      onClick={handleCancelEdit}
                      title="Cancel"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => setCurrentSessionId(session.id)}
                      className="w-full p-3 text-left"
                    >
                      <div className="mb-1 truncate text-sm font-medium">{session.title}</div>
                      <div className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(session.updated_at), { addSuffix: true })}
                      </div>
                    </button>
                    <div className="absolute right-2 top-2 hidden gap-1 group-hover:flex">
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-7 w-7"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStartEdit(session.id, session.title);
                        }}
                        title="Edit title"
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-7 w-7 text-destructive hover:text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(session.id);
                        }}
                        title="Delete chat"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="py-8 text-center text-sm text-muted-foreground">
            No chats yet. Start a new conversation!
          </div>
        )}
      </ScrollArea>

      <div className="border-t p-4">
        <Button
          variant="ghost"
          className="w-full justify-start"
          onClick={() => openModal('settings')}
        >
          <Settings className="mr-2 h-4 w-4" />
          <span className="truncate">{user?.name || 'Settings'}</span>
        </Button>
      </div>
    </div>
  );
}
