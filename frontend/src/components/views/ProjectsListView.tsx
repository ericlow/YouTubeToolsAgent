import { useState } from 'react';
import { FolderKanban } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { MobileHeader } from '@/components/layout/MobileHeader';
import { ProjectCard } from '@/components/projects/ProjectCard';
import { EmptyState } from '@/components/common/EmptyState';
import { NewProjectModal } from '@/components/modals/NewProjectModal';
import { ScrollArea } from '@/components/ui/scroll-area';
import { motion } from 'framer-motion';

export function ProjectsListView() {
  const { projects, setCurrentProject, deleteProject } = useAppStore();
  const [showNewProject, setShowNewProject] = useState(false);

  return (
    <div className="flex flex-col h-full">
      <MobileHeader
        title="Projects"
        showMenu
        showAdd
        onAdd={() => setShowNewProject(true)}
      />

      <ScrollArea className="flex-1">
        {projects.length === 0 ? (
          <EmptyState
            icon={<FolderKanban className="w-10 h-10 text-primary" />}
            title="Start your first research project"
            description="Create a project to organize and analyze YouTube videos with AI"
            actionLabel="Create Project"
            onAction={() => setShowNewProject(true)}
            className="min-h-[60vh]"
          />
        ) : (
          <div className="p-4 space-y-3 pb-20">
            {projects.map((project, index) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <ProjectCard
                  project={project}
                  onClick={() => setCurrentProject(project)}
                  onDelete={() => deleteProject(project.id)}
                />
              </motion.div>
            ))}
          </div>
        )}
      </ScrollArea>
      
      <NewProjectModal
        isOpen={showNewProject}
        onClose={() => setShowNewProject(false)}
      />
    </div>
  );
}
