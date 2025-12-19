import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';

interface FloatingActionButtonProps {
  onClick: () => void;
  label?: string;
}

export function FloatingActionButton({ onClick, label = 'Add Video' }: FloatingActionButtonProps) {
  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="fixed bottom-24 right-4 z-30 md:bottom-6 md:right-6 lg:hidden"
    >
      <Button
        onClick={onClick}
        size="lg"
        className="h-14 w-14 rounded-full elevation-4 touch-feedback gap-2"
      >
        <Plus className="w-6 h-6" />
        <span className="sr-only">{label}</span>
      </Button>
    </motion.div>
  );
}
