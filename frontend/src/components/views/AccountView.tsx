import { ChevronRight, User, CreditCard, Settings, LogOut } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { MobileHeader } from '@/components/layout/MobileHeader';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

const menuItems = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'billing', label: 'Billing', icon: CreditCard },
  { id: 'preferences', label: 'Preferences', icon: Settings },
];

export function AccountView() {
  const { user, setUser } = useAppStore();

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <div className="flex flex-col h-full">
      <MobileHeader title="Account" />
      
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-6 pb-20">
          {/* User Info */}
          <div className="flex items-center gap-4 p-4 bg-card border rounded-lg">
            <Avatar className="w-16 h-16">
              <AvatarImage src={user?.avatar} />
              <AvatarFallback className="text-lg bg-primary text-primary-foreground">
                {user?.name?.charAt(0) || 'U'}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <h2 className="font-semibold text-lg truncate">{user?.name || 'Guest User'}</h2>
              <p className="text-sm text-muted-foreground truncate">{user?.email || 'Not signed in'}</p>
            </div>
          </div>
          
          {/* Menu Items */}
          <div className="bg-card border rounded-lg overflow-hidden divide-y">
            {menuItems.map((item) => (
              <button
                key={item.id}
                className={cn(
                  'w-full flex items-center justify-between p-4',
                  'hover:bg-accent transition-colors touch-feedback'
                )}
              >
                <div className="flex items-center gap-3">
                  <item.icon className="w-5 h-5 text-muted-foreground" />
                  <span className="font-medium">{item.label}</span>
                </div>
                <ChevronRight className="w-5 h-5 text-muted-foreground" />
              </button>
            ))}
          </div>
          
          {/* Logout */}
          <Button
            variant="outline"
            className="w-full justify-start gap-3 h-12 text-destructive hover:text-destructive hover:bg-destructive/10"
            onClick={handleLogout}
          >
            <LogOut className="w-5 h-5" />
            Log out
          </Button>
        </div>
      </ScrollArea>
    </div>
  );
}
