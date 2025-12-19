import { X, ChevronDown, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Video } from '@/types';
import { Button } from '@/components/ui/button';
import { AspectRatio } from '@/components/ui/aspect-ratio';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { cn } from '@/lib/utils';

interface VideoPlayerModalProps {
  video: Video | null;
  isOpen: boolean;
  onClose: () => void;
  onRemove?: () => void;
}

export function VideoPlayerModal({ video, isOpen, onClose, onRemove }: VideoPlayerModalProps) {
  if (!video) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-background z-50 md:bg-background/80 md:backdrop-blur-sm"
            onClick={onClose}
          />
          
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            drag="y"
            dragConstraints={{ top: 0 }}
            dragElastic={0.2}
            onDragEnd={(_, info) => {
              if (info.offset.y > 100) onClose();
            }}
            className={cn(
              'fixed inset-0 z-50 bg-card overflow-y-auto',
              'md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2',
              'md:w-full md:max-w-3xl md:max-h-[90vh] md:rounded-2xl md:elevation-4'
            )}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 flex items-center justify-between p-4 glass z-10 safe-top">
              <div className="w-10 h-1 rounded-full bg-muted-foreground/30 absolute left-1/2 -translate-x-1/2 top-2 md:hidden" />
              <div />
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="w-5 h-5" />
              </Button>
            </div>
            
            {/* Video Player */}
            <div className="w-full bg-muted">
              <AspectRatio ratio={16 / 9}>
                <img
                  src={video.thumbnail}
                  alt={video.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-sm text-muted-foreground">Video player would go here</div>
                </div>
              </AspectRatio>
            </div>
            
            {/* Content */}
            <div className="p-4 space-y-4 safe-bottom">
              <div>
                <h2 className="font-semibold text-xl leading-tight">{video.title}</h2>
                <p className="text-sm text-muted-foreground mt-2">
                  {video.channelName} • {video.publishedAt} • {video.duration}
                </p>
              </div>
              
              <Accordion type="single" collapsible>
                <AccordionItem value="transcript">
                  <AccordionTrigger className="text-sm font-medium">
                    View Transcript
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="text-sm text-muted-foreground space-y-2 max-h-48 overflow-y-auto">
                      <p>[0:00] Welcome to this video. Today we're going to explore...</p>
                      <p>[0:15] The main topics we'll cover include...</p>
                      <p>[0:30] Let's start with the first concept...</p>
                      <p className="text-center italic">Transcript would continue here...</p>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>
              
              <Button
                variant="outline"
                className="w-full text-destructive hover:text-destructive hover:bg-destructive/10"
                onClick={() => {
                  onRemove?.();
                  onClose();
                }}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Remove from Project
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
