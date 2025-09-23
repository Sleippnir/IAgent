-- Migración: Crear tabla para almacenar análisis y métricas de entrevistas
-- Fecha: $(date)
-- Descripción: Tabla para almacenar métricas, análisis y evaluaciones de las entrevistas

CREATE TABLE IF NOT EXISTS public.interview_analytics (
    id_analytics SERIAL PRIMARY KEY,
    id_interview INTEGER NOT NULL,
    
    -- Métricas de tiempo
    total_duration_seconds INTEGER,
    candidate_speaking_time_seconds INTEGER,
    interviewer_speaking_time_seconds INTEGER,
    silence_time_seconds INTEGER,
    interruptions_count INTEGER DEFAULT 0,
    
    -- Métricas de contenido
    total_words INTEGER,
    candidate_words INTEGER,
    interviewer_words INTEGER,
    questions_count INTEGER DEFAULT 0,
    answers_count INTEGER DEFAULT 0,
    
    -- Análisis de sentimiento
    overall_sentiment_score DECIMAL(3,2) CHECK (overall_sentiment_score >= -1 AND overall_sentiment_score <= 1),
    candidate_sentiment_score DECIMAL(3,2) CHECK (candidate_sentiment_score >= -1 AND candidate_sentiment_score <= 1),
    interviewer_sentiment_score DECIMAL(3,2) CHECK (interviewer_sentiment_score >= -1 AND interviewer_sentiment_score <= 1),
    
    -- Análisis de emociones
    dominant_emotion VARCHAR(20),
    emotion_distribution JSONB,
    
    -- Métricas de calidad
    audio_quality_score DECIMAL(3,2) CHECK (audio_quality_score >= 0 AND audio_quality_score <= 1),
    transcription_confidence DECIMAL(3,2) CHECK (transcription_confidence >= 0 AND transcription_confidence <= 1),
    
    -- Análisis de competencias
    technical_keywords TEXT[],
    soft_skills_detected TEXT[],
    competency_scores JSONB,
    
    -- Evaluación general
    overall_score DECIMAL(3,2) CHECK (overall_score >= 0 AND overall_score <= 1),
    recommendation VARCHAR(20) CHECK (recommendation IN ('hire', 'reject', 'second_interview', 'pending')),
    strengths TEXT[],
    weaknesses TEXT[],
    key_insights TEXT,
    
    -- Metadatos y configuración
    analysis_version VARCHAR(10) DEFAULT '1.0',
    processing_engine VARCHAR(50) DEFAULT 'custom',
    processing_time_seconds INTEGER,
    is_final BOOLEAN DEFAULT FALSE,
    reviewed_by INTEGER,
    review_notes TEXT,
    metadata JSONB,
    
    timestamp_created TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    timestamp_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_analytics_interview 
        FOREIGN KEY (id_interview) 
        REFERENCES public.interviews(id_interview) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_analytics_reviewer 
        FOREIGN KEY (reviewed_by) 
        REFERENCES public.users(id_user) 
        ON DELETE SET NULL
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_interview_analytics_interview_id ON public.interview_analytics(id_interview);
CREATE INDEX IF NOT EXISTS idx_interview_analytics_recommendation ON public.interview_analytics(recommendation);
CREATE INDEX IF NOT EXISTS idx_interview_analytics_overall_score ON public.interview_analytics(overall_score);
CREATE INDEX IF NOT EXISTS idx_interview_analytics_sentiment ON public.interview_analytics(overall_sentiment_score);
CREATE INDEX IF NOT EXISTS idx_interview_analytics_final ON public.interview_analytics(is_final);
CREATE INDEX IF NOT EXISTS idx_interview_analytics_created ON public.interview_analytics(timestamp_created);

-- Índices para búsquedas en arrays
CREATE INDEX IF NOT EXISTS idx_interview_analytics_technical_keywords 
    ON public.interview_analytics 
    USING gin(technical_keywords);
    
CREATE INDEX IF NOT EXISTS idx_interview_analytics_soft_skills 
    ON public.interview_analytics 
    USING gin(soft_skills_detected);
    
CREATE INDEX IF NOT EXISTS idx_interview_analytics_strengths 
    ON public.interview_analytics 
    USING gin(strengths);
    
CREATE INDEX IF NOT EXISTS idx_interview_analytics_weaknesses 
    ON public.interview_analytics 
    USING gin(weaknesses);

-- Trigger para actualizar timestamp_updated automáticamente
CREATE TRIGGER trigger_update_interview_analytics_timestamp
    BEFORE UPDATE ON public.interview_analytics
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp_updated();

-- Comentarios para documentación
COMMENT ON TABLE public.interview_analytics IS 'Almacena análisis, métricas y evaluaciones de las entrevistas';
COMMENT ON COLUMN public.interview_analytics.id_analytics IS 'Identificador único del análisis';
COMMENT ON COLUMN public.interview_analytics.id_interview IS 'Referencia a la entrevista';
COMMENT ON COLUMN public.interview_analytics.total_duration_seconds IS 'Duración total de la entrevista en segundos';
COMMENT ON COLUMN public.interview_analytics.candidate_speaking_time_seconds IS 'Tiempo que habló el candidato';
COMMENT ON COLUMN public.interview_analytics.interviewer_speaking_time_seconds IS 'Tiempo que habló el entrevistador';
COMMENT ON COLUMN public.interview_analytics.overall_sentiment_score IS 'Puntuación general de sentimiento (-1 a 1)';
COMMENT ON COLUMN public.interview_analytics.emotion_distribution IS 'Distribución de emociones en formato JSON';
COMMENT ON COLUMN public.interview_analytics.competency_scores IS 'Puntuaciones de competencias en formato JSON';
COMMENT ON COLUMN public.interview_analytics.overall_score IS 'Puntuación general de la entrevista (0-1)';
COMMENT ON COLUMN public.interview_analytics.recommendation IS 'Recomendación: hire, reject, second_interview, pending';
COMMENT ON COLUMN public.interview_analytics.technical_keywords IS 'Palabras clave técnicas detectadas';
COMMENT ON COLUMN public.interview_analytics.soft_skills_detected IS 'Habilidades blandas detectadas';
COMMENT ON COLUMN public.interview_analytics.key_insights IS 'Insights clave del análisis';
COMMENT ON COLUMN public.interview_analytics.is_final IS 'Indica si es el análisis final';
COMMENT ON COLUMN public.interview_analytics.metadata IS 'Metadatos adicionales en formato JSON';