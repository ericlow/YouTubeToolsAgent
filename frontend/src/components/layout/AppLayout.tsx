import { useState } from 'react';
import { useAppStore } from '@/store/appStore';
import { useIsDesktop, useIsTablet } from '@/hooks/useMediaQuery';
import { MobileNav } from '@/components/layout/MobileNav';
import { DesktopSidebar } from '@/components/layout/DesktopSidebar';
import { ProjectsListView } from '@/components/views/ProjectsListView';
import { ProjectDetailView } from '@/components/views/ProjectDetailView';
import { AccountView } from '@/components/views/AccountView';
import { AuthView } from '@/components/auth/AuthView';
import { NewProjectModal } from '@/components/modals/NewProjectModal';

export function AppLayout() {
  const { isAuthenticated, activeTab, currentProject } = useAppStore();
  const isDesktop = useIsDesktop();
  const isTablet = useIsTablet();
  const [showNewProject, setShowNewProject] = useState(false);

  // Show auth if not authenticated
  if (!isAuthenticated) {
    return <AuthView />;
  }

  // Mobile view
  if (!isDesktop && !isTablet) {
    return (
      <div className="h-screen flex flex-col overflow-hidden">
        <div className="flex-1 overflow-hidden pb-16">
          {activeTab === 'projects' && (
            currentProject ? (
              <ProjectDetailView />
            ) : (
              <ProjectsListView />
            )
          )}
          {activeTab === 'account' && <AccountView />}
        </div>
        <MobileNav />
      </div>
    );
  }

  // Tablet view
  if (isTablet) {
    return (
      <div className="h-screen flex overflow-hidden">
        <DesktopSidebar onNewProject={() => setShowNewProject(true)} />
        <main className="flex-1 overflow-hidden">
          {currentProject ? (
            <ProjectDetailView />
          ) : activeTab === 'account' ? (
            <AccountView />
          ) : (
            <ProjectsListView />
          )}
        </main>
        
        <NewProjectModal
          isOpen={showNewProject}
          onClose={() => setShowNewProject(false)}
        />
      </div>
    );
  }

  // Desktop view
  return (
    <div className="h-screen flex overflow-hidden">
      <DesktopSidebar onNewProject={() => setShowNewProject(true)} />
      <main className="flex-1 overflow-hidden">
        {currentProject ? (
          <ProjectDetailView />
        ) : activeTab === 'account' ? (
          <AccountView />
        ) : (
          <ProjectsListView />
        )}
      </main>
      
      <NewProjectModal
        isOpen={showNewProject}
        onClose={() => setShowNewProject(false)}
      />
    </div>
  );
}
