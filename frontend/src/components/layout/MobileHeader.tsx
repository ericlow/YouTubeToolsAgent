import { Menu, Plus, ArrowLeft, MoreVertical, MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/store/appStore';

interface MobileHeaderProps {
  title?: string;
  showBack?: boolean;
  showMenu?: boolean;
  showAdd?: boolean;
  showMore?: boolean;
  showChat?: boolean;
  onBack?: () => void;
  onMenu?: () => void;
  onAdd?: () => void;
  onMore?: () => void;
  onChat?: () => void;
}

export function MobileHeader({
  title = 'Projects',
  showBack = false,
  showMenu = false,
  showAdd = false,
  showMore = false,
  showChat = false,
  onBack,
  onMenu,
  onAdd,
  onMore,
  onChat,
}: MobileHeaderProps) {
  return (
    <header className="sticky top-0 z-40 glass border-b safe-top md:hidden">
      <div className="flex items-center justify-between h-14 px-4">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          {showBack && (
            <Button variant="ghost" size="icon" onClick={onBack} className="shrink-0">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          )}
          {showMenu && (
            <Button variant="ghost" size="icon" onClick={onMenu} className="shrink-0">
              <Menu className="w-5 h-5" />
            </Button>
          )}
          <h1 className="font-semibold text-lg truncate">{title}</h1>
        </div>
        
        <div className="flex items-center gap-1 shrink-0">
          {showChat && (
            <Button variant="ghost" size="icon" onClick={onChat}>
              <MessageCircle className="w-5 h-5" />
            </Button>
          )}
          {showAdd && (
            <Button variant="ghost" size="sm" onClick={onAdd} className="gap-1">
              <Plus className="w-4 h-4" />
              <span className="text-sm">New</span>
            </Button>
          )}
          {showMore && (
            <Button variant="ghost" size="icon" onClick={onMore}>
              <MoreVertical className="w-5 h-5" />
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
