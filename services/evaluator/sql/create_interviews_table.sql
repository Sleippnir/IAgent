-- SQL script to create the interviews table in Supabase
-- Run this in your Supabase SQL editor to create the table

CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    interview_id VARCHAR(255) UNIQUE NOT NULL,
    system_prompt TEXT,
    rubric TEXT,
    jd TEXT,
    full_transcript TEXT,
    evaluation_1 TEXT,
    evaluation_2 TEXT,
    evaluation_3 TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index on interview_id for faster lookups
CREATE INDEX idx_interviews_interview_id ON interviews(interview_id);

-- Create a trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_interviews_updated_at 
    BEFORE UPDATE ON interviews 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow all operations for authenticated users
-- Adjust this policy based on your security requirements
CREATE POLICY "Allow all operations for authenticated users" ON interviews
    FOR ALL USING (auth.role() = 'authenticated');

-- Optional: Create a policy for anonymous access (if needed)
-- CREATE POLICY "Allow read access for anonymous users" ON interviews
--     FOR SELECT USING (true);