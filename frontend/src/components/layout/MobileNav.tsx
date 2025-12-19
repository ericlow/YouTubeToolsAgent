import { FolderKanban, User } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

const tabs = [
  { id: 'projects' as const, label: 'Projects', icon: FolderKanban },
  { id: 'account' as const, label: 'Account', icon: User },
];

export function MobileNav() {
  const { activeTab, setActiveTab } = useAppStore();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 glass border-t safe-bottom md:hidden">
      <div className="flex items-center justify-around h-16">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex flex-col items-center justify-center w-full h-full gap-1 touch-feedback',
                'transition-colors duration-200'
              )}
            >
              <div className="relative">
                <tab.icon
                  className={cn(
                    'w-6 h-6 transition-colors duration-200',
                    isActive ? 'text-nav-active' : 'text-muted-foreground'
                  )}
                />
                {isActive && (
                  <motion.div
                    layoutId="nav-indicator"
                    className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-nav-active"
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
              </div>
              <span
                className={cn(
                  'text-xs font-medium transition-colors duration-200',
                  isActive ? 'text-nav-active' : 'text-muted-foreground'
                )}
              >
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
