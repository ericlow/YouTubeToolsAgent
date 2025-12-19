import { ChevronRight, Trash2 } from 'lucide-react';
import { Project } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion';
import { useState } from 'react';
import { cn } from '@/lib/utils';

interface ProjectCardProps {
  project: Project;
  onClick: () => void;
  onDelete?: () => void;
}

export function ProjectCard({ project, onClick, onDelete }: ProjectCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const x = useMotionValue(0);
  const background = useTransform(x, [-100, 0], ['hsl(var(--destructive))', 'transparent']);
  const deleteOpacity = useTransform(x, [-100, -50, 0], [1, 0.5, 0]);

  const handleDragEnd = (_: any, info: PanInfo) => {
    if (info.offset.x < -100 && onDelete) {
      setIsDeleting(true);
      onDelete();
    }
  };

  return (
    <div className="relative overflow-hidden rounded-lg">
      {/* Delete background */}
      <motion.div
        className="absolute inset-y-0 right-0 flex items-center justify-end px-6"
        style={{ background, opacity: deleteOpacity }}
      >
        <Trash2 className="w-5 h-5 text-destructive-foreground" />
      </motion.div>

      {/* Card content */}
      <motion.div
        drag="x"
        dragConstraints={{ left: -100, right: 0 }}
        dragElastic={0.1}
        onDragEnd={handleDragEnd}
        style={{ x }}
        onClick={onClick}
        className={cn(
          'relative flex items-center gap-4 p-4 bg-card border rounded-lg cursor-pointer',
          'touch-feedback hover:border-primary/20 hover:elevation-2 transition-all duration-200'
        )}
      >
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-base truncate">{project.title}</h3>
          <p className="text-sm text-muted-foreground mt-1">
            {project.videoCount} videos • {formatDistanceToNow(project.updatedAt, { addSuffix: true })}
          </p>
        </div>
        <ChevronRight className="w-5 h-5 text-muted-foreground shrink-0" />
      </motion.div>
    </div>
  );
}
