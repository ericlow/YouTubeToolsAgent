import { useState } from 'react';
import { Video, Sparkles, Send, Plus } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { MobileHeader } from '@/components/layout/MobileHeader';
import { VideoCard } from '@/components/videos/VideoCard';
import { EmptyState } from '@/components/common/EmptyState';
import { AddVideoModal } from '@/components/modals/AddVideoModal';
import { VideoPlayerModal } from '@/components/modals/VideoPlayerModal';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Video as VideoType } from '@/types';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ProjectDetailViewProps {
  onOpenVideos?: () => void;
}

export function ProjectDetailView({ onOpenVideos }: ProjectDetailViewProps) {
  const { currentProject, setCurrentProject, videos, removeVideo, messages, addMessage } = useAppStore();
  const [showAddVideo, setShowAddVideo] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<VideoType | null>(null);
  const [showVideos, setShowVideos] = useState(false);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    
    addMessage({
      id: Date.now().toString(),
      content: input,
      role: 'user',
      timestamp: new Date(),
    });
    setInput('');
    
    // Simulate AI response
    setTimeout(() => {
      addMessage({
        id: (Date.now() + 1).toString(),
        content: 'This is a simulated AI response. In a real implementation, this would be connected to an AI service to analyze your videos and provide insights.',
        role: 'assistant',
        timestamp: new Date(),
      });
    }, 1000);
  };

  if (!currentProject) return null;

  return (
    <div className="flex flex-col h-full">
      <MobileHeader
        title={currentProject.title}
        showBack
        showMore
        onBack={() => setCurrentProject(null)}
      />
      
      {/* Desktop header */}
      <div className="hidden md:flex items-center justify-between h-14 px-4 border-b">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          <span className="font-semibold">{currentProject.title}</span>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="gap-2"
          onClick={() => setShowVideos(true)}
        >
          <Video className="w-4 h-4" />
          Videos ({videos.length})
        </Button>
      </div>
      
      {/* Chat as main content */}
      <ScrollArea className="flex-1 p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-6">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Start a conversation</h3>
            <p className="text-muted-foreground text-sm max-w-[250px]">
              Ask questions about your videos and get AI-powered insights
            </p>
            <div className="mt-6 space-y-2 w-full max-w-[280px]">
              {['Summarize key points', 'Find common themes', 'Compare videos'].map((q) => (
                <button
                  key={q}
                  onClick={() => setInput(q)}
                  className="w-full text-left text-sm p-3 rounded-lg bg-accent hover:bg-accent/80 transition-colors touch-feedback"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {message.role === 'assistant' && (
                  <Avatar className="w-8 h-8 shrink-0">
                    <AvatarFallback className="bg-primary text-primary-foreground text-xs">AI</AvatarFallback>
                  </Avatar>
                )}
                <div
                  className={cn(
                    'max-w-[80%] rounded-2xl px-4 py-3 text-sm',
                    message.role === 'user'
                      ? 'bg-chat-user text-chat-user-foreground rounded-br-md'
                      : 'bg-chat-ai text-chat-ai-foreground rounded-bl-md'
                  )}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
                {message.role === 'user' && (
                  <Avatar className="w-8 h-8 shrink-0">
                    <AvatarFallback className="bg-secondary text-secondary-foreground text-xs">U</AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}
          </div>
        )}
      </ScrollArea>

      {/* Chat Input */}
      <div className="p-4 border-t">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your videos..."
            className="flex-1"
          />
          <Button type="submit" size="icon" disabled={!input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
      
      {/* Floating Videos Button (mobile) */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setShowVideos(true)}
        className="md:hidden fixed bottom-24 right-4 z-30 w-14 h-14 rounded-full bg-primary text-primary-foreground shadow-lg flex items-center justify-center"
      >
        <Video className="w-6 h-6" />
      </motion.button>
      
      {/* Videos Overlay/Modal */}
      {showVideos && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40"
            onClick={() => setShowVideos(false)}
          />
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed inset-x-0 bottom-0 top-16 md:top-0 md:right-0 md:left-auto md:w-[450px] z-50 bg-card rounded-t-xl md:rounded-l-xl md:rounded-tr-none overflow-hidden flex flex-col"
          >
            <div className="flex items-center justify-between h-14 px-4 border-b">
              <div className="flex items-center gap-2">
                <Video className="w-5 h-5 text-primary" />
                <span className="font-semibold">Videos ({videos.length})</span>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-1"
                  onClick={() => setShowAddVideo(true)}
                >
                  <Plus className="w-4 h-4" />
                  Add
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setShowVideos(false)}>
                  Close
                </Button>
              </div>
            </div>
            
            <ScrollArea className="flex-1 p-4">
              {videos.length === 0 ? (
                <EmptyState
                  icon={<Video className="w-10 h-10 text-primary" />}
                  title="Add videos to begin"
                  description="Paste YouTube URLs to add videos to your research project"
                  actionLabel="Add Video"
                  onAction={() => setShowAddVideo(true)}
                  className="py-12"
                />
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {videos.map((video, index) => (
                    <motion.div
                      key={video.id}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <VideoCard
                        video={video}
                        onClick={() => setSelectedVideo(video)}
                      />
                    </motion.div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </motion.div>
        </>
      )}
      
      <AddVideoModal
        isOpen={showAddVideo}
        onClose={() => setShowAddVideo(false)}
      />
      
      <VideoPlayerModal
        video={selectedVideo}
        isOpen={!!selectedVideo}
        onClose={() => setSelectedVideo(null)}
        onRemove={() => selectedVideo && removeVideo(selectedVideo.id)}
      />
    </div>
  );
}
