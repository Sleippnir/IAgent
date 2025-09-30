-- Migration: 007_create_jobs_table
-- Description: Create jobs table for job positions
-- Author: System Migration
-- Date: 2025-01-27

-- Create jobs table
CREATE TABLE IF NOT EXISTS public.jobs (
    id_job SERIAL PRIMARY KEY,
    job_role VARCHAR(100) NOT NULL,
    description TEXT,
    timestamp_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add comments for documentation
COMMENT ON TABLE public.jobs IS 'Table storing job positions available for interviews';
COMMENT ON COLUMN public.jobs.id_job IS 'Primary key for job identification';
COMMENT ON COLUMN public.jobs.job_role IS 'Title or role name of the job position';
COMMENT ON COLUMN public.jobs.description IS 'Detailed description of the job requirements and responsibilities';
COMMENT ON COLUMN public.jobs.timestamp_created IS 'Timestamp when the job was created';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jobs_role ON public.jobs(job_role);
CREATE INDEX IF NOT EXISTS idx_jobs_timestamp ON public.jobs(timestamp_created);
CREATE INDEX IF NOT EXISTS idx_jobs_description ON public.jobs USING gin(to_tsvector('english', description));

-- Enable Row Level Security (RLS)
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- Create policy for public read access
CREATE POLICY "Anyone can view jobs" ON public.jobs
    FOR SELECT USING (true);

-- Create policy for admin management
CREATE POLICY "Admin can manage jobs" ON public.jobs
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Grant permissions
GRANT SELECT ON public.jobs TO anon, authenticated;
GRANT ALL ON public.jobs TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.jobs_id_job_seq TO anon, authenticated, service_role;