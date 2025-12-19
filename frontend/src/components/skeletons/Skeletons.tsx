import { cn } from '@/lib/utils';

interface VideoCardSkeletonProps {
  className?: string;
}

export function VideoCardSkeleton({ className }: VideoCardSkeletonProps) {
  return (
    <div className={cn('bg-card border rounded-lg overflow-hidden', className)}>
      <div className="aspect-video skeleton-pulse" />
      <div className="p-3 space-y-2">
        <div className="h-4 skeleton-pulse rounded w-full" />
        <div className="h-4 skeleton-pulse rounded w-3/4" />
        <div className="h-3 skeleton-pulse rounded w-1/2 mt-3" />
      </div>
    </div>
  );
}

export function ProjectCardSkeleton() {
  return (
    <div className="flex items-center gap-4 p-4 bg-card border rounded-lg">
      <div className="flex-1 space-y-2">
        <div className="h-5 skeleton-pulse rounded w-3/4" />
        <div className="h-4 skeleton-pulse rounded w-1/2" />
      </div>
      <div className="w-5 h-5 skeleton-pulse rounded" />
    </div>
  );
}
