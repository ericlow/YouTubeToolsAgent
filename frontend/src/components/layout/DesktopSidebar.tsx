import { FolderKanban, MessageCircle, Settings, Plus, Search, ChevronRight } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { formatDistanceToNow } from 'date-fns';

interface DesktopSidebarProps {
  onNewProject?: () => void;
}

export function DesktopSidebar({ onNewProject }: DesktopSidebarProps) {
  const { projects, currentProject, setCurrentProject, setActiveTab, activeTab } = useAppStore();

  return (
    <aside className="hidden md:flex flex-col w-[280px] h-full border-r bg-card">
      {/* Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <Search className="w-4 h-4 text-primary-foreground" />
          </div>
          <span className="font-semibold text-lg">VideoResearch</span>
        </div>
      </div>

      {/* Navigation */}
      <div className="p-3 space-y-1">
        <Button
          variant={activeTab === 'projects' && !currentProject ? 'secondary' : 'ghost'}
          className="w-full justify-start gap-3"
          onClick={() => {
            setActiveTab('projects');
            setCurrentProject(null);
          }}
        >
          <FolderKanban className="w-4 h-4" />
          All Projects
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start gap-3"
          onClick={() => setActiveTab('account')}
        >
          <Settings className="w-4 h-4" />
          Settings
        </Button>
      </div>

      {/* Projects List */}
      <div className="flex items-center justify-between px-4 py-2 border-t">
        <span className="text-sm font-medium text-muted-foreground">Projects</span>
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onNewProject}>
          <Plus className="w-4 h-4" />
        </Button>
      </div>

      <ScrollArea className="flex-1 px-2">
        <div className="space-y-1 pb-4">
          {projects.map((project) => (
            <button
              key={project.id}
              onClick={() => {
                setCurrentProject(project);
                setActiveTab('projects');
              }}
              className={cn(
                'w-full flex items-center justify-between p-3 rounded-lg transition-all duration-200',
                'hover:bg-accent group touch-feedback',
                currentProject?.id === project.id && 'bg-accent'
              )}
            >
              <div className="flex-1 text-left min-w-0">
                <p className="font-medium truncate">{project.title}</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {project.videoCount} videos • {formatDistanceToNow(project.updatedAt, { addSuffix: true })}
                </p>
              </div>
              <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
            </button>
          ))}
        </div>
      </ScrollArea>
    </aside>
  );
}
