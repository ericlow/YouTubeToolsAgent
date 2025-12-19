import { Send, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { useAppStore } from '@/store/appStore';
import { MobileHeader } from '@/components/layout/MobileHeader';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

export function ChatView() {
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
    
    setTimeout(() => {
      addMessage({
        id: (Date.now() + 1).toString(),
        content: 'This is a simulated AI response. In a real implementation, this would analyze your video content and provide insights.',
        role: 'assistant',
        timestamp: new Date(),
      });
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full">
      <MobileHeader title="Chat" />
      
      <ScrollArea className="flex-1">
        <div className="p-4 pb-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                <Sparkles className="w-10 h-10 text-primary" />
              </div>
              <h3 className="font-semibold text-xl mb-2">Start a conversation</h3>
              <p className="text-muted-foreground text-sm max-w-[280px] mb-6">
                Ask questions about your videos and get AI-powered insights
              </p>
              <div className="space-y-2 w-full max-w-[300px]">
                {['What are the key takeaways?', 'Find common themes', 'Summarize all videos'].map((q) => (
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
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.02 }}
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
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </ScrollArea>
      
      {/* Input area */}
      <div className="p-4 border-t bg-card safe-bottom">
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
            className="flex-1 h-12"
          />
          <Button type="submit" size="icon" className="h-12 w-12" disabled={!input.trim()}>
            <Send className="w-5 h-5" />
          </Button>
        </form>
      </div>
    </div>
  );
}
