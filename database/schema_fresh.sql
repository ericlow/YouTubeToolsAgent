-- WARNING: DESTRUCTIVE - Drops all tables and data
-- Use only during development when you want a fresh start

DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS workspace_videos CASCADE;
DROP TABLE IF EXISTS videos CASCADE;
DROP TABLE IF EXISTS workspaces CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create tables fresh
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workspaces (
    workspace_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE videos (
    video_id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    transcript TEXT NOT NULL,
    title VARCHAR(500) NOT NULL,
    channel VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workspace_videos (
    workspace_id UUID REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(video_id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summary TEXT,
    PRIMARY KEY (workspace_id, video_id)
);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(video_id) ON DELETE SET NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_messages_workspace_id ON messages(workspace_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_videos_url ON videos(url);