import { X, Send, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '@/store/appStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

interface ChatPanelProps {
  isOpen?: boolean;
  onClose?: () => void;
  isOverlay?: boolean;
}

export function ChatPanel({ isOpen = true, onClose, isOverlay = false }: ChatPanelProps) {
  const { messages, addMessage } = useAppStore();
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

  const content = (
    <div className={cn(
      'flex flex-col h-full bg-card',
      isOverlay && 'rounded-l-xl elevation-4'
    )}>
      {/* Header */}
      <div className="flex items-center justify-between h-14 px-4 border-b">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-primary" />
          <span className="font-semibold">AI Chat</span>
        </div>
        {onClose && (
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Messages */}
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

      {/* Input */}
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
    </div>
  );

  if (isOverlay) {
    return (
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40"
              onClick={onClose}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="fixed right-0 top-0 bottom-0 w-[400px] z-50"
            >
              {content}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    );
  }

  return <div className="hidden lg:block w-[350px] border-l h-full">{content}</div>;
}
