-- Migration: 011_create_technical_questions_answers_table
-- Description: Create technical_questions_answers table for technical interview questions
-- Author: System Migration
-- Date: 2025-01-27

-- Create technical_questions_answers table
CREATE TABLE IF NOT EXISTS public.technical_questions_answers (
    id_tech_question_answer SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    timestamp_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add comments for documentation
COMMENT ON TABLE public.technical_questions_answers IS 'Table storing technical interview questions and their expected answers';
COMMENT ON COLUMN public.technical_questions_answers.id_tech_question_answer IS 'Primary key for technical question identification';
COMMENT ON COLUMN public.technical_questions_answers.question IS 'Technical interview question text';
COMMENT ON COLUMN public.technical_questions_answers.answer IS 'Expected or sample answer for the technical question';
COMMENT ON COLUMN public.technical_questions_answers.timestamp_created IS 'Timestamp when the question was created';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_technical_questions_timestamp ON public.technical_questions_answers(timestamp_created);
CREATE INDEX IF NOT EXISTS idx_technical_questions_search ON public.technical_questions_answers USING gin(to_tsvector('english', question || ' ' || answer));

-- Enable Row Level Security (RLS)
ALTER TABLE public.technical_questions_answers ENABLE ROW LEVEL SECURITY;

-- Create policy for admin management
CREATE POLICY "Admin can manage technical questions" ON public.technical_questions_answers
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Create policy for interviewer access
CREATE POLICY "Interviewers can view technical questions" ON public.technical_questions_answers
    FOR SELECT USING (auth.jwt() ->> 'role' IN ('admin', 'interviewer'));

-- Grant permissions
GRANT SELECT ON public.technical_questions_answers TO authenticated;
GRANT ALL ON public.technical_questions_answers TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.technical_questions_answers_id_tech_question_answer_seq TO authenticated, service_role;