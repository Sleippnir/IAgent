-- Migration: 012_create_technical_questions_answers_jobs_table
-- Description: Create technical_questions_answers_jobs table for job-specific technical questions
-- Author: System Migration
-- Date: 2025-01-27
-- Dependencies: 007_create_jobs_table.sql, 011_create_technical_questions_answers_table.sql

-- Create technical_questions_answers_jobs table
CREATE TABLE IF NOT EXISTS public.technical_questions_answers_jobs (
    id_tech_question_answer SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    id_job INTEGER,
    timestamp_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint (optional reference to jobs)
    CONSTRAINT fk_tech_questions_jobs 
        FOREIGN KEY (id_job) 
        REFERENCES public.jobs(id_job) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
);

-- Add comments for documentation
COMMENT ON TABLE public.technical_questions_answers_jobs IS 'Table storing job-specific technical interview questions and their expected answers';
COMMENT ON COLUMN public.technical_questions_answers_jobs.id_tech_question_answer IS 'Primary key for job-specific technical question identification';
COMMENT ON COLUMN public.technical_questions_answers_jobs.question IS 'Job-specific technical interview question text';
COMMENT ON COLUMN public.technical_questions_answers_jobs.answer IS 'Expected or sample answer for the job-specific technical question';
COMMENT ON COLUMN public.technical_questions_answers_jobs.id_job IS 'Optional foreign key referencing jobs table for job-specific questions';
COMMENT ON COLUMN public.technical_questions_answers_jobs.timestamp_created IS 'Timestamp when the question was created';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tech_questions_jobs_job ON public.technical_questions_answers_jobs(id_job);
CREATE INDEX IF NOT EXISTS idx_tech_questions_jobs_timestamp ON public.technical_questions_answers_jobs(timestamp_created);
CREATE INDEX IF NOT EXISTS idx_tech_questions_jobs_search ON public.technical_questions_answers_jobs USING gin(to_tsvector('english', question || ' ' || answer));

-- Enable Row Level Security (RLS)
ALTER TABLE public.technical_questions_answers_jobs ENABLE ROW LEVEL SECURITY;

-- Create policy for admin management
CREATE POLICY "Admin can manage job technical questions" ON public.technical_questions_answers_jobs
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Create policy for interviewer access
CREATE POLICY "Interviewers can view job technical questions" ON public.technical_questions_answers_jobs
    FOR SELECT USING (auth.jwt() ->> 'role' IN ('admin', 'interviewer'));

-- Grant permissions
GRANT SELECT ON public.technical_questions_answers_jobs TO authenticated;
GRANT ALL ON public.technical_questions_answers_jobs TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.technical_questions_answers_jobs_id_tech_question_answer_seq TO authenticated, service_role;