-- Migration: 010_create_general_questions_answers_table
-- Description: Create general_questions_answers table for general interview questions
-- Author: System Migration
-- Date: 2025-01-27

-- Create general_questions_answers table
CREATE TABLE IF NOT EXISTS public.general_questions_answers (
    id_gral_question_answer SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    timestamp_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add comments for documentation
COMMENT ON TABLE public.general_questions_answers IS 'Table storing general interview questions and their expected answers';
COMMENT ON COLUMN public.general_questions_answers.id_gral_question_answer IS 'Primary key for general question identification';
COMMENT ON COLUMN public.general_questions_answers.question IS 'General interview question text';
COMMENT ON COLUMN public.general_questions_answers.answer IS 'Expected or sample answer for the question';
COMMENT ON COLUMN public.general_questions_answers.timestamp_created IS 'Timestamp when the question was created';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_general_questions_timestamp ON public.general_questions_answers(timestamp_created);
CREATE INDEX IF NOT EXISTS idx_general_questions_search ON public.general_questions_answers USING gin(to_tsvector('english', question || ' ' || answer));

-- Enable Row Level Security (RLS)
ALTER TABLE public.general_questions_answers ENABLE ROW LEVEL SECURITY;

-- Create policy for admin management
CREATE POLICY "Admin can manage general questions" ON public.general_questions_answers
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Create policy for interviewer access
CREATE POLICY "Interviewers can view general questions" ON public.general_questions_answers
    FOR SELECT USING (auth.jwt() ->> 'role' IN ('admin', 'interviewer'));

-- Grant permissions
GRANT SELECT ON public.general_questions_answers TO authenticated;
GRANT ALL ON public.general_questions_answers TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.general_questions_answers_id_gral_question_answer_seq TO authenticated, service_role;