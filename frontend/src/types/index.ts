export interface Project {
  id: string;
  title: string;
  videoCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Video {
  id: string;
  title: string;
  thumbnail: string;
  channelName: string;
  duration: string;
  publishedAt: string;
  url: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}
