import { Play } from 'lucide-react';
import { Video } from '@/types';
import { cn } from '@/lib/utils';
import { AspectRatio } from '@/components/ui/aspect-ratio';

interface VideoCardProps {
  video: Video;
  onClick: () => void;
}

export function VideoCard({ video, onClick }: VideoCardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'group bg-card border rounded-lg overflow-hidden cursor-pointer',
        'touch-feedback hover:elevation-2 hover:border-primary/20 transition-all duration-200'
      )}
    >
      {/* Thumbnail */}
      <div className="relative">
        <AspectRatio ratio={16 / 9}>
          <img
            src={video.thumbnail}
            alt={video.title}
            className="w-full h-full object-cover"
          />
        </AspectRatio>
        
        {/* Play overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-background/20 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="w-14 h-14 rounded-full bg-background/90 flex items-center justify-center elevation-2">
            <Play className="w-6 h-6 text-foreground ml-1" fill="currentColor" />
          </div>
        </div>
        
        {/* Duration badge */}
        <div className="absolute bottom-2 right-2 px-2 py-1 rounded-md bg-background/90 text-xs font-medium">
          {video.duration}
        </div>
      </div>

      {/* Content */}
      <div className="p-3">
        <h3 className="font-medium text-sm line-clamp-2 leading-snug">{video.title}</h3>
        <p className="text-xs text-muted-foreground mt-2">
          {video.channelName} • {video.publishedAt}
        </p>
      </div>
    </div>
  );
}
