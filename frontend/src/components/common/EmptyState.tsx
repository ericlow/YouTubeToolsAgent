import { FolderPlus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className,
}: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center text-center p-8', className)}>
      {icon && (
        <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-6">
          {icon}
        </div>
      )}
      <h3 className="font-semibold text-xl mb-2">{title}</h3>
      {description && (
        <p className="text-muted-foreground text-sm max-w-[280px] mb-6">{description}</p>
      )}
      {actionLabel && onAction && (
        <Button onClick={onAction} className="gap-2">
          <FolderPlus className="w-4 h-4" />
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
