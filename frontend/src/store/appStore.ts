import { create } from 'zustand';
import { Project, Video, ChatMessage, User } from '@/types';

interface AppState {
  // Auth
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  
  // Projects
  projects: Project[];
  currentProject: Project | null;
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  addProject: (project: Project) => void;
  deleteProject: (id: string) => void;
  
  // Videos
  videos: Video[];
  setVideos: (videos: Video[]) => void;
  addVideo: (video: Video) => void;
  removeVideo: (id: string) => void;
  
  // Chat
  messages: ChatMessage[];
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  
  // UI State
  activeTab: 'projects' | 'account';
  setActiveTab: (tab: 'projects' | 'account') => void;
  isChatOpen: boolean;
  setChatOpen: (open: boolean) => void;
}

// Mock data
const mockProjects: Project[] = [
  { id: '1', title: 'AI Startup Research', videoCount: 8, createdAt: new Date(Date.now() - 86400000 * 2), updatedAt: new Date(Date.now() - 86400000) },
  { id: '2', title: 'Product Design Inspiration', videoCount: 12, createdAt: new Date(Date.now() - 86400000 * 5), updatedAt: new Date(Date.now() - 86400000 * 3) },
  { id: '3', title: 'Marketing Strategies', videoCount: 5, createdAt: new Date(Date.now() - 86400000 * 10), updatedAt: new Date(Date.now() - 86400000 * 7) },
];

const mockVideos: Video[] = [
  { id: '1', title: 'How to Build an AI Startup in 2024 - Complete Guide', thumbnail: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=640&h=360&fit=crop', channelName: 'Tech Founders', duration: '24:35', publishedAt: '2 weeks ago', url: 'https://youtube.com/watch?v=example1' },
  { id: '2', title: 'The Future of Machine Learning: Trends & Predictions', thumbnail: 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=640&h=360&fit=crop', channelName: 'AI Insights', duration: '18:42', publishedAt: '1 month ago', url: 'https://youtube.com/watch?v=example2' },
  { id: '3', title: 'Building Products Users Love - Design Thinking', thumbnail: 'https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?w=640&h=360&fit=crop', channelName: 'Design Masters', duration: '32:10', publishedAt: '3 weeks ago', url: 'https://youtube.com/watch?v=example3' },
  { id: '4', title: 'Scaling Your Startup from 0 to $1M ARR', thumbnail: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=640&h=360&fit=crop', channelName: 'Startup School', duration: '45:20', publishedAt: '1 week ago', url: 'https://youtube.com/watch?v=example4' },
];

const mockMessages: ChatMessage[] = [
  { id: '1', content: 'What are the main themes across these videos?', role: 'user', timestamp: new Date(Date.now() - 60000 * 5) },
  { id: '2', content: 'Based on the videos in your project, there are several key themes:\n\n1. **AI & Technology Trends** - Multiple videos discuss the future of AI and machine learning\n2. **Startup Growth** - There\'s a focus on scaling and building sustainable businesses\n3. **User-Centric Design** - Design thinking and product development best practices', role: 'assistant', timestamp: new Date(Date.now() - 60000 * 4) },
];

export const useAppStore = create<AppState>((set) => ({
  // Auth - Demo user for preview
  user: { id: '1', name: 'Demo User', email: 'demo@example.com' },
  isAuthenticated: true,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  
  // Projects
  projects: mockProjects,
  currentProject: null,
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (currentProject) => set({ currentProject }),
  addProject: (project) => set((state) => ({ projects: [project, ...state.projects] })),
  deleteProject: (id) => set((state) => ({ projects: state.projects.filter((p) => p.id !== id) })),
  
  // Videos
  videos: mockVideos,
  setVideos: (videos) => set({ videos }),
  addVideo: (video) => set((state) => ({ videos: [...state.videos, video] })),
  removeVideo: (id) => set((state) => ({ videos: state.videos.filter((v) => v.id !== id) })),
  
  // Chat
  messages: mockMessages,
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  
  // UI State
  activeTab: 'projects',
  setActiveTab: (activeTab) => set({ activeTab }),
  isChatOpen: false,
  setChatOpen: (isChatOpen) => set({ isChatOpen }),
}));
