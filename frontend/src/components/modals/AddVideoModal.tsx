import { useState } from 'react';
import { X, Link2, Search, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';

interface AddVideoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AddVideoModal({ isOpen, onClose }: AddVideoModalProps) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { addVideo } = useAppStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please enter a YouTube URL');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));
    
    addVideo({
      id: Date.now().toString(),
      title: 'New Video Added',
      thumbnail: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=640&h=360&fit=crop',
      channelName: 'Channel Name',
      duration: '10:30',
      publishedAt: 'Just added',
      url: url,
    });
    
    setIsLoading(false);
    setUrl('');
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50"
          />
          
          {/* Modal */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={cn(
              'fixed bottom-0 left-0 right-0 z-50',
              'bg-card rounded-t-2xl elevation-4',
              'max-h-[80vh] overflow-hidden'
            )}
          >
            {/* Handle */}
            <div className="flex justify-center pt-3 pb-2">
              <div className="w-10 h-1 rounded-full bg-muted-foreground/30" />
            </div>
            
            {/* Header */}
            <div className="flex items-center justify-between px-4 pb-4 border-b">
              <h2 className="text-lg font-semibold">Add Video</h2>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="w-5 h-5" />
              </Button>
            </div>
            
            {/* Content */}
            <div className="p-4 space-y-6 safe-bottom">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="video-url" className="flex items-center gap-2">
                    <Link2 className="w-4 h-4" />
                    Paste YouTube URL
                  </Label>
                  <Input
                    id="video-url"
                    value={url}
                    onChange={(e) => {
                      setUrl(e.target.value);
                      setError('');
                    }}
                    placeholder="https://youtube.com/watch?v=..."
                    className={cn('h-12', error && 'border-destructive')}
                    autoFocus
                  />
                  {error && <p className="text-sm text-destructive">{error}</p>}
                </div>
                
                <Button type="submit" className="w-full h-12" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Adding video...
                    </>
                  ) : (
                    'Add Video'
                  )}
                </Button>
              </form>
              
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">or</span>
                </div>
              </div>
              
              <Button variant="outline" className="w-full h-12 gap-2">
                <Search className="w-4 h-4" />
                Search YouTube Videos
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
