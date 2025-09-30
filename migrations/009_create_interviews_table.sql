-- Migration: 009_create_interviews_table
-- Description: Create interviews table for scheduled interviews
-- Author: System Migration
-- Date: 2025-01-27
-- Dependencies: 008_create_candidates_table.sql

-- Create interviews table
CREATE TABLE IF NOT EXISTS public.interviews (
    id_interview SERIAL PRIMARY KEY,
    id_candidate INTEGER NOT NULL,
    interview_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'scheduled',
    notes TEXT,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    timestamp_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_interviews_candidates 
        FOREIGN KEY (id_candidate) 
        REFERENCES public.candidates(id_candidate) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Add comments for documentation
COMMENT ON TABLE public.interviews IS 'Table storing interview schedules and results';
COMMENT ON COLUMN public.interviews.id_interview IS 'Primary key for interview identification';
COMMENT ON COLUMN public.interviews.id_candidate IS 'Foreign key referencing candidates table';
COMMENT ON COLUMN public.interviews.interview_date IS 'Scheduled date and time for the interview';
COMMENT ON COLUMN public.interviews.status IS 'Interview status (scheduled, completed, cancelled, no-show)';
COMMENT ON COLUMN public.interviews.notes IS 'Interview notes and observations';
COMMENT ON COLUMN public.interviews.score IS 'Interview score from 0 to 100';
COMMENT ON COLUMN public.interviews.timestamp_created IS 'Timestamp when the interview was scheduled';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_interviews_candidate ON public.interviews(id_candidate);
CREATE INDEX IF NOT EXISTS idx_interviews_date ON public.interviews(interview_date);
CREATE INDEX IF NOT EXISTS idx_interviews_status ON public.interviews(status);
CREATE INDEX IF NOT EXISTS idx_interviews_timestamp ON public.interviews(timestamp_created);
CREATE INDEX IF NOT EXISTS idx_interviews_score ON public.interviews(score);

-- Enable Row Level Security (RLS)
ALTER TABLE public.interviews ENABLE ROW LEVEL SECURITY;

-- Create policy for candidates to view their own interviews
CREATE POLICY "Candidates can view own interviews" ON public.interviews
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.candidates 
            JOIN public.users ON candidates.id_user = users.id_user
            WHERE candidates.id_candidate = interviews.id_candidate 
            AND auth.jwt() ->> 'user_id'::text = users.id_user::text
        )
    );

-- Create policy for admin access
CREATE POLICY "Admin can manage interviews" ON public.interviews
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Create policy for interviewers (if role exists)
CREATE POLICY "Interviewers can manage interviews" ON public.interviews
    FOR ALL USING (auth.jwt() ->> 'role' = 'interviewer');

-- Grant permissions
GRANT SELECT ON public.interviews TO authenticated;
GRANT ALL ON public.interviews TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.interviews_id_interview_seq TO authenticated, service_role;