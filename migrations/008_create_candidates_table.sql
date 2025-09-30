-- Migration: 008_create_candidates_table
-- Description: Create candidates table for job applicants
-- Author: System Migration
-- Date: 2025-01-27
-- Dependencies: 006_create_users_table.sql, 007_create_jobs_table.sql

-- Create candidates table
CREATE TABLE IF NOT EXISTS public.candidates (
    id_candidate SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL,
    id_job INTEGER NOT NULL,
    cv_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    timestamp_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_candidates_users 
        FOREIGN KEY (id_user) 
        REFERENCES public.users(id_user) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
        
    CONSTRAINT fk_candidates_jobs 
        FOREIGN KEY (id_job) 
        REFERENCES public.jobs(id_job) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
        
    -- Unique constraint to prevent duplicate applications
    CONSTRAINT uk_candidates_user_job UNIQUE (id_user, id_job)
);

-- Add comments for documentation
COMMENT ON TABLE public.candidates IS 'Table storing job candidates and their applications';
COMMENT ON COLUMN public.candidates.id_candidate IS 'Primary key for candidate identification';
COMMENT ON COLUMN public.candidates.id_user IS 'Foreign key referencing users table';
COMMENT ON COLUMN public.candidates.id_job IS 'Foreign key referencing jobs table';
COMMENT ON COLUMN public.candidates.cv_path IS 'File path to the candidate CV/resume';
COMMENT ON COLUMN public.candidates.status IS 'Application status (pending, approved, rejected, interviewed)';
COMMENT ON COLUMN public.candidates.timestamp_created IS 'Timestamp when the application was submitted';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_candidates_user ON public.candidates(id_user);
CREATE INDEX IF NOT EXISTS idx_candidates_job ON public.candidates(id_job);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON public.candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_timestamp ON public.candidates(timestamp_created);

-- Enable Row Level Security (RLS)
ALTER TABLE public.candidates ENABLE ROW LEVEL SECURITY;

-- Create policy for candidates to view their own applications
CREATE POLICY "Candidates can view own applications" ON public.candidates
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE users.id_user = candidates.id_user 
            AND auth.jwt() ->> 'user_id'::text = users.id_user::text
        )
    );

-- Create policy for admin access
CREATE POLICY "Admin can manage candidates" ON public.candidates
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Create policy for candidate registration
CREATE POLICY "Users can apply for jobs" ON public.candidates
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE users.id_user = candidates.id_user 
            AND auth.jwt() ->> 'user_id'::text = users.id_user::text
        )
    );

-- Grant permissions
GRANT SELECT ON public.candidates TO authenticated;
GRANT INSERT ON public.candidates TO authenticated;
GRANT ALL ON public.candidates TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.candidates_id_candidate_seq TO authenticated, service_role;