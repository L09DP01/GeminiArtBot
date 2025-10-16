/*
  # GeminiArtBot Database Schema

  ## Overview
  This migration creates the core database structure for the GeminiArtBot Telegram bot.
  The bot generates AI images based on user prompts and tracks credits for each user.

  ## New Tables

  ### 1. users
  Stores all registered Telegram users with their credit balance and language preference.
  - `id` (bigint, primary key) - Telegram user ID
  - `credits` (integer, default 3) - Number of image generation credits remaining
  - `language` (text, default 'en') - User's preferred language (en/fr)
  - `created_at` (timestamptz) - Registration timestamp

  ### 2. prompts
  Stores the history of all image generation requests.
  - `id` (uuid, primary key) - Unique prompt ID
  - `user_id` (bigint, foreign key) - References users table
  - `prompt_text` (text) - The text prompt submitted by user
  - `image_url` (text) - Generated image URL from OpenRouter API
  - `created_at` (timestamptz) - Request timestamp

  ## Security
  - Enable RLS on both tables
  - Users can only read their own data
  - Insert operations are restricted to authenticated service

  ## Indexes
  - Index on user_id in prompts table for faster query performance
  - Automatic timestamp indexing for historical queries
*/

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id bigint PRIMARY KEY,
  credits integer NOT NULL DEFAULT 3,
  language text NOT NULL DEFAULT 'en',
  created_at timestamptz DEFAULT now()
);

-- Create prompts table
CREATE TABLE IF NOT EXISTS prompts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  prompt_text text NOT NULL,
  image_url text,
  created_at timestamptz DEFAULT now()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON prompts(user_id);
CREATE INDEX IF NOT EXISTS idx_prompts_created_at ON prompts(created_at DESC);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can read own data"
  ON users FOR SELECT
  TO authenticated
  USING (auth.uid()::text::bigint = id);

CREATE POLICY "Service role can insert users"
  ON users FOR INSERT
  TO service_role
  WITH CHECK (true);

CREATE POLICY "Service role can update users"
  ON users FOR UPDATE
  TO service_role
  USING (true)
  WITH CHECK (true);

-- RLS Policies for prompts table
CREATE POLICY "Users can read own prompts"
  ON prompts FOR SELECT
  TO authenticated
  USING (auth.uid()::text::bigint = user_id);

CREATE POLICY "Service role can insert prompts"
  ON prompts FOR INSERT
  TO service_role
  WITH CHECK (true);

CREATE POLICY "Service role can read all prompts"
  ON prompts FOR SELECT
  TO service_role
  USING (true);